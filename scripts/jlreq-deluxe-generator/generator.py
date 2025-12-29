import copy
from dataclasses import dataclass
import logging
from pathlib import Path

from jfm import JFM
from kpse import find_file
from utils import to_fixed_str
from virtual_font import CharacterPacket, FontDefinition, SimpleDvi, VF

logger = logging.getLogger(__name__)


@dataclass
class Config:
    tfmdir: Path
    vfdir: Path
    dumpjpl: bool
    jpldir: Path
    dumpvpl: bool
    vpldir: Path


JLREQ_VARIANTS = ["", "b", "z", "bz"]
OTF_VARIANTS = [("nml", ""), ("nml", "n"), ("exp", ""), ("exp", "n"), ("ruby", "")]
OTF_FAMILIES = ["minl", "minr", "minb", "gothr", "gothb", "gotheb", "mgothr"]
PXUFONT_VARIANTS = [("nml", ""), ("nml", "n"), ("ruby", "")]


def generate_all(config: Config):
    for jv in JLREQ_VARIANTS:
        for ov, on in OTF_VARIANTS:
            for of in OTF_FAMILIES:
                j_name = f"{jv}jlreq"
                o_name = f"{ov}{of}{on}-h"
                d_name = f"{jv}jlreq--{ov}{of}{on}-h"
                generate(j_name, o_name, d_name, config)

                j_name = f"{jv}jlreq-v"
                o_name = f"{ov}{of}{on}-v"
                d_name = f"{jv}jlreq--{ov}{of}{on}-v"
                generate(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq"
                o_name = f"up{ov}{of}{on}-h"
                d_name = f"{jv}jlreq--up{ov}{of}{on}-h"
                generate(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq-v"
                o_name = f"up{ov}{of}{on}-v"
                d_name = f"{jv}jlreq--up{ov}{of}{on}-v"
                generate(j_name, o_name, d_name, config)

    for jv in JLREQ_VARIANTS:
        for ov, on in PXUFONT_VARIANTS:
            for of in OTF_FAMILIES:
                j_name = f"{jv}jlreq"
                o_name = f"zu-{ov}{of}{on}-h"
                d_name = f"zu-{jv}jlreq--{ov}{of}{on}-h"
                generate(j_name, o_name, d_name, config)

                j_name = f"{jv}jlreq-v"
                o_name = f"zu-{ov}{of}{on}-v"
                d_name = f"zu-{jv}jlreq--{ov}{of}{on}-v"
                generate(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq"
                o_name = f"zu-up{ov}{of}{on}-h"
                d_name = f"zu-{jv}jlreq--up{ov}{of}{on}-h"
                generate(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq-v"
                o_name = f"zu-up{ov}{of}{on}-v"
                d_name = f"zu-{jv}jlreq--up{ov}{of}{on}-v"
                generate(j_name, o_name, d_name, config)


def generate(j_name, o_name, d_name, config: Config):
    # jlreqのJFMを読み込み
    j_jfm_name = find_file(f"{j_name}.tfm")
    j_jfm = JFM()
    logger.info(f"Load {j_jfm_name}")
    j_jfm.load(j_jfm_name)

    # otfのJFMを読み込み
    o_jfm_name = find_file(f"{o_name}.tfm")
    o_jfm = JFM()
    logger.info(f"Load {o_jfm_name}")
    o_jfm.load(o_jfm_name)

    # 文字タイプ0の文字幅が異なっているときはエラー
    if j_jfm.get_type_width(0) != o_jfm.get_type_width(0):
        logger.error("TYPE 0 CHARWD missmatch!!")
        return False

    # jlreqのVFを読み込み
    j_vf_name = find_file(f"{j_name}.vf")
    j_vf = VF()
    logger.info(f"Load {j_vf_name}")
    j_vf.load(j_vf_name)

    # otfのVFを読み込み
    o_vf_name = find_file(f"{o_name}.vf")
    o_vf = VF()
    logger.info(f"Load {o_vf_name}")
    o_vf.load(o_vf_name)

    # jlreq-deluxe用のJFMを作成する（jlreqからコピー）
    d_jfm = copy.deepcopy(j_jfm)
    d_jfm.check_sum = 0

    # jlreq-deluxe用のVFを作成する
    # デザインサイズはjlreqと同じ
    # フォント0にotfのフォントを指定しデフォルトになるようにする
    d_vf = VF()
    d_vf.comment = f"{d_name}".encode("ascii")
    d_vf.design_size = j_jfm.design_size
    d_vf.font_definitions[0] = FontDefinition(
        o_jfm.check_sum,
        o_jfm.design_size / j_jfm.design_size,
        o_jfm.design_size,
        f"{o_name}".encode("ascii"),
    )
    d_vf.default_font_num = 0

    # jlreqとotfのJFMに含まれる文字一覧を取得（重複削除）
    kanji_list = sorted(
        list(set(j_jfm.chars_type.keys()) | set(o_jfm.chars_type.keys()))
    )
    for k in kanji_list:
        j_wd = j_jfm.get_char_width(k)
        o_wd = o_jfm.get_char_width(k)
        if j_wd != o_wd:
            logger.debug(
                f"H {k:04X} CHARWD {to_fixed_str(j_wd)} <=> {to_fixed_str(o_wd)}"
            )
            move_right = 0.0
            if j_wd < o_wd:
                dvi = j_vf.get_char_simple_dvi(k)
                if dvi and dvi.move_right:
                    move_right = dvi.move_right
                    logger.debug(f" jlreq: MOVERIGHT R {to_fixed_str(move_right)}")

                    move_right = (j_wd - o_wd) * move_right / (j_wd - j_jfm.zw)
                    logger.debug(f"     => MOVERIGHT R {to_fixed_str(move_right)}")
            else:  # j_wd > o_wd:
                dvi = o_vf.get_char_simple_dvi(k)
                if dvi and dvi.move_right:
                    move_right = dvi.move_right
                    logger.debug(f"   otf: MOVERIGHT R {to_fixed_str(move_right)})")

                    move_right = (j_wd - o_wd) * move_right / (o_wd - o_jfm.zw)
                    logger.debug(f"     => MOVERIGHT R {to_fixed_str(move_right)}")

            d_vf.char_packets[k] = CharacterPacket(j_wd, SimpleDvi(None, move_right, k))

    if config.dumpjpl:
        with open(config.jpldir / f"{d_name}.jpl", "w") as writer:
            d_jfm.dump(writer)

    if config.dumpvpl:
        with open(config.vpldir / f"{d_name}.vpl", "w") as writer:
            d_vf.dump(writer)

    d_jfm_name = config.tfmdir / f"{d_name}.tfm"
    logger.info(f"Save {d_jfm_name}")
    d_jfm.save(d_jfm_name)

    d_vf_name = config.vfdir / f"{d_name}.vf"
    logger.info(f"Save {d_vf_name}")
    d_vf.save(d_vf_name)
