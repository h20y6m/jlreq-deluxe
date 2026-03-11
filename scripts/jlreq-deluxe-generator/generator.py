import copy
from dataclasses import dataclass
import logging
from pathlib import Path

from jfm import JFM
from kpse import find_file
from utils import f_near, to_fixed_str
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
JLREQ_FAMILIES = ["", "g"]
OTF_VARIANTS = [("nml", ""), ("nml", "n"), ("exp", ""), ("exp", "n"), ("ruby", "")]
OTF_FAMILIES = ["minl", "minr", "minb", "gothr", "gothb", "gotheb", "mgothr"]
PXUFONT_VARIANTS = [("nml", ""), ("nml", "n"), ("ruby", "")]


def generate_all(config: Config):
    generate_deluxe(config)
    generate_ufont(config)


def generate_deluxe(config: Config):
    for jv in JLREQ_VARIANTS:
        for ov, on in OTF_VARIANTS:
            for of in OTF_FAMILIES:
                j_name = f"{jv}jlreq"
                o_name = f"{ov}{of}{on}-h"
                d_name = f"{jv}jlreq--{ov}{of}{on}-h"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"{jv}jlreq-v"
                o_name = f"{ov}{of}{on}-v"
                d_name = f"{jv}jlreq--{ov}{of}{on}-v"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq"
                o_name = f"up{ov}{of}{on}-h"
                d_name = f"{jv}jlreq--up{ov}{of}{on}-h"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq-v"
                o_name = f"up{ov}{of}{on}-v"
                d_name = f"{jv}jlreq--up{ov}{of}{on}-v"
                generate_one(j_name, o_name, d_name, config)


def generate_ufont(config: Config):
    for jv in JLREQ_VARIANTS:
        for jf in JLREQ_FAMILIES:
            j_name = f"{jv}jlreq"
            u_name = f"zu-jis{jf}"
            d_name = f"zu-{jv}jlreq{jf}"
            generate_one(j_name, u_name, d_name, config)

            j_name = f"{jv}jlreq-v"
            u_name = f"zu-jis{jf}-v"
            d_name = f"zu-{jv}jlreq{jf}-v"
            generate_one(j_name, u_name, d_name, config)

    for jv in JLREQ_VARIANTS:
        for ov, on in PXUFONT_VARIANTS:
            for of in OTF_FAMILIES:
                j_name = f"{jv}jlreq"
                o_name = f"zu-{ov}{of}{on}-h"
                d_name = f"zu-{jv}jlreq--{ov}{of}{on}-h"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"{jv}jlreq-v"
                o_name = f"zu-{ov}{of}{on}-v"
                d_name = f"zu-{jv}jlreq--{ov}{of}{on}-v"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq"
                o_name = f"zu-up{ov}{of}{on}-h"
                d_name = f"zu-{jv}jlreq--up{ov}{of}{on}-h"
                generate_one(j_name, o_name, d_name, config)

                j_name = f"u{jv}jlreq-v"
                o_name = f"zu-up{ov}{of}{on}-v"
                d_name = f"zu-{jv}jlreq--up{ov}{of}{on}-v"
                generate_one(j_name, o_name, d_name, config)


def generate_one(j_name, o_name, d_name, config: Config):
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

    # 文字タイプ0の文字幅が全角じゃない！
    if j_jfm.get_type_width(0) != j_jfm.zw:
        logger.error(f"TYPE 0 CHARWD not 1zw!! ({j_name})")
        return
    if o_jfm.get_type_width(0) != o_jfm.zw:
        logger.error(f"TYPE 0 CHARWD not 1zw!! ({o_name})")
        return

    # 全角幅が異なっている！
    scale = 1.0
    if j_jfm.zw != o_jfm.zw:
        scale = j_jfm.zw / o_jfm.zw
        logger.warning(f"1zw missmatch!! scale to {j_jfm.zw} / {o_jfm.zw} = {scale}")

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
        o_jfm.design_size / j_jfm.design_size * scale,
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
        j_wd_zw = j_wd / j_jfm.zw
        o_wd_zw = o_wd / o_jfm.zw
        if not f_near(j_wd_zw, o_wd_zw):
            logger.debug(
                f"diff: {k:04X}: {to_fixed_str(j_wd_zw)}zw vs {to_fixed_str(o_wd_zw)}zw"
            )
            move_right = 0.0
            if not f_near(j_wd_zw, 1.0):
                dvi = j_vf.get_char_simple_dvi(k)
                if dvi and dvi.move_right:
                    move_right = dvi.move_right / j_jfm.zw
                    logger.debug(f"   j: {to_fixed_str(move_right)}zw")
                    move_right = (
                        move_right * j_jfm.zw * (o_wd_zw - j_wd_zw) / (1.0 - j_wd_zw)
                    )
                    logger.debug(f"   => {to_fixed_str(move_right)}")
            elif not f_near(o_wd, 1.0):
                dvi = o_vf.get_char_simple_dvi(k)
                if dvi and dvi.move_right:
                    move_right = dvi.move_right / o_jfm.zw
                    logger.debug(f"   o: {to_fixed_str(move_right)}zw")
                    move_right = (
                        -move_right * j_jfm.zw * (j_wd_zw - o_wd_zw) / (1.0 - o_wd_zw)
                    )
                    logger.debug(f"   => {to_fixed_str(move_right)}")
            else:
                logger.warning(
                    f"diff: {k:04X}: {to_fixed_str(j_wd_zw)}zw vs {to_fixed_str(o_wd_zw)}zw"
                )

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
    # JFM().load(d_jfm_name)

    d_vf_name = config.vfdir / f"{d_name}.vf"
    logger.info(f"Save {d_vf_name}")
    d_vf.save(d_vf_name)
