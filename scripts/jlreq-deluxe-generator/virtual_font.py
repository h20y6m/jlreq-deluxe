from dataclasses import dataclass
import io
import logging
from typing import BinaryIO, Dict, TextIO

from binaryio import BinaryReader, BinaryWriter
from utils import b2i, b2u, from_fixed, to_fixed, to_fixed_str

logger = logging.getLogger(__name__)


DVI_SET_CHAR_0 = 0
DVI_SET1 = 128
DVI_SET_RULE = 132
DVI_PUT1 = 133
DVI_PUT_RULE = 137
DVI_NOP = 138
DVI_PUSH = 141
DVI_POP = 142
DVI_RIGHT1 = 143
DVI_W0 = 147
DVI_W1 = 148
DVI_X0 = 152
DVI_X1 = 153
DVI_DOWN1 = 157
DVI_Y0 = 161
DVI_Y1 = 162
DVI_Z0 = 166
DVI_Z1 = 167
DVI_FNT_NUM_0 = 171
DVI_FNT1 = 235
DVI_XXX1 = 239


@dataclass
class SimpleDvi:
    select_font: int | None = None
    move_right: float | None = None
    set_char: int | None = None

    def to_dvi(self) -> bytes:
        buf = io.BytesIO()
        writer = BinaryWriter(buf)

        if self.select_font is not None:
            if self.select_font < 0:
                writer.write_u8(DVI_FNT1 + 3)
                writer.write_i32(self.select_font)
            elif self.select_font < 64:
                writer.write_u8(DVI_FNT_NUM_0 + self.select_font)
            elif self.select_font < 256:
                writer.write_u8(DVI_FNT1)
                writer.write_u8(self.select_font)
            elif self.select_font < (1 << 16):
                writer.write_u8(DVI_FNT1 + 1)
                writer.write_u16(self.select_font)
            elif self.select_font < (1 << 24):
                writer.write_u8(DVI_FNT1 + 2)
                writer.write_u24(self.select_font)
            else:
                writer.write_u8(DVI_FNT1 + 3)
                writer.write_i32(self.select_font)

        if self.move_right is not None and self.move_right != 0.0:
            x = to_fixed(self.move_right)
            if abs(x) < 128:
                writer.write_u8(DVI_RIGHT1)
                writer.write_i8(x)
            elif abs(x) < (1 << 15):
                writer.write_u8(DVI_RIGHT1 + 1)
                writer.write_i16(x)
            elif abs(x) < (1 << 23):
                writer.write_u8(DVI_RIGHT1 + 2)
                writer.write_i24(x)
            else:
                writer.write_u8(DVI_RIGHT1 + 3)
                writer.write_i32(x)

        if self.set_char is not None:
            if self.set_char < 128:
                writer.write_u8(DVI_SET_CHAR_0 + self.set_char)
            elif self.set_char < (1 << 8):
                writer.write_u8(DVI_SET1)
                writer.write_u8(self.set_char)
            elif self.set_char < (1 << 16):
                writer.write_u8(DVI_SET1 + 1)
                writer.write_u16(self.set_char)
            elif self.set_char < (1 << 24):
                writer.write_u8(DVI_SET1 + 2)
                writer.write_u24(self.set_char)
            else:
                writer.write_u8(DVI_RIGHT1 + 3)
                writer.write_i32(self.set_char)

        return buf.getvalue()


def parse_simple_dvi(dvi):
    fnt = None
    h, w, x = 0.0, 0.0, 0.0
    simple_dvi = None

    buf = dvi
    while len(buf) > 0:
        if buf[0] < DVI_SET1:
            cc = buf[0]
            buf = buf[1:]
            if simple_dvi is not None:
                return None
            simple_dvi = SimpleDvi(fnt, h, cc)
        elif buf[0] >= DVI_SET1 and buf[0] < DVI_SET_RULE:
            n = buf[0] - DVI_SET1 + 1
            if n < 4:
                cc = b2u(buf[1 : 1 + n])
            else:
                cc = b2i(buf[1 : 1 + n])
            buf = buf[1 + n :]
            if simple_dvi is not None:
                return None
            simple_dvi = SimpleDvi(fnt, h, cc)
        elif buf[0] >= DVI_PUT1 and buf[0] < DVI_PUT_RULE:
            n = buf[0] - DVI_PUT1 + 1
            if n < 4:
                cc = b2u(buf[1 : 1 + n])
            else:
                cc = b2i(buf[1 : 1 + n])
            buf = buf[1 + n :]
            if simple_dvi is not None:
                return None
            simple_dvi = SimpleDvi(fnt, h, cc)
        elif buf[0] >= DVI_FNT_NUM_0 and buf[0] < DVI_FNT1:
            fnt = buf[0] - DVI_FNT_NUM_0
            buf = buf[1:]
        elif buf[0] >= DVI_FNT1 and buf[0] < DVI_XXX1:
            n = buf[0] - DVI_FNT1 + 1
            if n < 4:
                fnt = b2u(buf[1 : 1 + n])
            else:
                fnt = b2i(buf[1 : 1 + n])
            buf = buf[1 + n :]
        elif buf[0] >= DVI_RIGHT1 and buf[0] < DVI_W0:
            n = buf[0] - DVI_RIGHT1 + 1
            h += from_fixed(b2i(buf[1 : 1 + n]))
            buf = buf[1 + n :]
        elif buf[0] == DVI_W0:
            h += w
            buf = buf[1:]
        elif buf[0] >= DVI_W1 and buf[0] < DVI_X0:
            n = buf[0] - DVI_W1 + 1
            w = from_fixed(b2i(buf[1 : 1 + n]))
            h += w
            buf = buf[1 + n :]
        elif buf[0] == DVI_X0:
            h += x
            buf = buf[1:]
        elif buf[0] >= DVI_X1 and buf[0] < DVI_DOWN1:
            n = buf[0] - DVI_X1 + 1
            x = from_fixed(b2i(buf[1 : 1 + n]))
            h += x
            buf = buf[1 + n :]
        else:
            return None

    return simple_dvi


@dataclass
class FontDefinition:
    check_sum: int
    scaled_size: float
    design_size: float
    name: bytes


@dataclass
class CharacterPacket:
    character_width: float
    dvi: bytes | SimpleDvi


VF_ID_BYTE = 202
VF_LONG_CHAR = 242
VF_FNT_DEF1 = 243
VF_PRE = 247
VF_POST = 248


class BadVF(Exception):
    pass


class VF:
    def __init__(self):
        self.comment: bytes = b""
        self.check_sum: int = 0
        self.design_size: float = 0.0
        self.font_definitions: Dict[int, FontDefinition] = {}
        self.char_packets: Dict[int, CharacterPacket] = {}
        self.default_font_num: int | None = None

    def get_char_simple_dvi(self, k: int) -> SimpleDvi | None:
        if k in self.char_packets:
            char_packet = self.char_packets[k]
            if isinstance(char_packet.dvi, SimpleDvi):
                return char_packet.dvi
        return None

    def load(self, file: str | BinaryIO):
        """VFファイルを読み込む。"""
        with BinaryReader(file) as reader:
            command = reader.read_u8()
            if command != VF_PRE:
                raise BadVF("File is not a VF file")
            i = reader.read_u8()
            if i != VF_ID_BYTE:
                raise BadVF("File is not a VF file")
            k = reader.read_u8()
            x = reader.read_bytes(k)
            cs = reader.read_u32()
            ds = reader.read_f12d20()
            self.comment = x
            self.check_sum = cs
            self.design_size = ds
            logger.debug(f"pre {command} {k} {x} {cs} {ds}")

            command = reader.read_u8()
            while command >= VF_FNT_DEF1 and command < VF_FNT_DEF1 + 4:
                x = command - VF_FNT_DEF1 + 1
                if x < 4:
                    k = reader.read_u(x)
                else:
                    k = reader.read_i(x)
                c = reader.read_u32()
                s = reader.read_f12d20()
                d = reader.read_f12d20()
                a = reader.read_u8()
                l = reader.read_u8()  # noqa: E741
                n = reader.read_bytes(a + l)
                logger.debug(f"fnt_def{x} {command} {k} {c} {s} {d} {a} {l} {n}")
                self.font_definitions[k] = FontDefinition(
                    check_sum=c, scaled_size=s, design_size=d, name=n
                )
                if self.default_font_num is None:
                    if k != 0:
                        logger.info(f"The font {k} is first-defined font.")
                    self.default_font_num = k

                command = reader.read_u8()

            while command <= VF_LONG_CHAR:
                if command < VF_LONG_CHAR:
                    pl = command
                    cc = reader.read_u8()
                    tfm = reader.read_f4d20()
                    dvi = reader.read_bytes(pl)
                    logger.debug(f"short_char{pl} {pl} 0x{cc:02X} {tfm} {dvi}")
                else:
                    pl = reader.read_u32()
                    cc = reader.read_u32()
                    tfm = reader.read_f12d20()
                    dvi = reader.read_bytes(pl)
                    logger.debug(f"long_char {command} {pl} 0x{cc:04X} {tfm} {dvi}")

                if cc in self.char_packets:
                    logger.warning(f"Duplicate character packet {cc} ignored!")

                simple_dvi = parse_simple_dvi(dvi)
                if simple_dvi is None:
                    raise NotImplementedError("Non-simple DVI")

                self.char_packets[cc] = CharacterPacket(
                    character_width=tfm, dvi=simple_dvi
                )

                command = reader.read_u8()

            if command != VF_POST:
                raise BadVF(f"Bad command {command}")

            postamble = reader.read_all()
            if len(postamble) > 3 or not all(c == VF_POST for c in postamble):
                raise BadVF("Bad postamble")

    def _is_trivial_char(self, cc):
        """指定した文字がデフォルトフォントの同一文字を単純に出力するものであれば`True`を返す。"""
        dvi = self.char_packets[cc].dvi
        if not isinstance(dvi, SimpleDvi):
            return False
        if dvi.select_font is not None and dvi.select_font != self.default_font_num:
            return False
        if dvi.move_right is not None and dvi.move_right != 0.0:
            return False
        if dvi.set_char != cc:
            return False
        return True

    def compact(self):
        """VF軽量化（和文VFのfallback機能向け）。"""
        self.char_packets = {
            cc: cp
            for cc, cp in self.char_packets.items()
            if not self._is_trivial_char(cc)
        }

    def save(self, file):
        """VFファイルを書き出す。"""
        with BinaryWriter(file) as writer:
            writer.write_u8(VF_PRE)
            writer.write_u8(VF_ID_BYTE)
            k = len(self.comment)
            if k >= 256:
                raise BadVF("Too long comment.")
            writer.write_u8(k)
            writer.write_bytes(self.comment)
            writer.write_u32(self.check_sum)
            writer.write_f12d20(self.design_size)

            # font definitions
            if self.default_font_num is not None:
                self._write_fnt_def(writer, self.default_font_num)
            for fnt_num in sorted(self.font_definitions.keys()):
                if fnt_num != self.default_font_num:
                    self._write_fnt_def(writer, fnt_num)

            # character packets
            for cc in sorted(self.char_packets.keys()):
                p = self.char_packets[cc]
                if isinstance(p.dvi, SimpleDvi):
                    dvi = p.dvi.to_dvi()
                else:
                    dvi = p.dvi
                pl = len(dvi)
                tfm = to_fixed(p.character_width)
                if pl < 242 and cc < 256 and tfm >= 0 and tfm < (1 << 24):
                    logger.debug(
                        f"short_char{pl} {pl} {cc} {to_fixed_str(p.character_width)} {dvi}"
                    )
                    writer.write_u8(pl)
                    writer.write_u8(cc)
                    writer.write_u24(tfm)
                else:
                    logger.debug(
                        f"long_char {pl} {cc} {to_fixed_str(p.character_width)} {dvi}"
                    )
                    writer.write_u8(VF_LONG_CHAR)
                    writer.write_u32(pl)
                    writer.write_u32(cc)
                    writer.write_i32(tfm)
                writer.write_bytes(dvi)

            # postamble
            n = 4 - writer.size % 4
            writer.write_bytes(bytes([VF_POST] * n))

    def _write_fnt_def(self, writer: BinaryWriter, fnt_num: int):
        fnt_def = self.font_definitions[fnt_num]
        if fnt_num < 0:
            writer.write_u8(VF_FNT_DEF1 + 3)
            writer.write_i32(fnt_num)
        elif fnt_num < 256:
            writer.write_u8(VF_FNT_DEF1)
            writer.write_u8(fnt_num)
        elif fnt_num < (1 << 16):
            writer.write_u8(VF_FNT_DEF1 + 1)
            writer.write_u16(fnt_num)
        elif fnt_num < (1 << 24):
            writer.write_u8(VF_FNT_DEF1 + 2)
            writer.write_u16(fnt_num)
        else:
            writer.write_u8(VF_FNT_DEF1 + 3)
            writer.write_i32(fnt_num)
        writer.write_u32(fnt_def.check_sum)
        writer.write_f12d20(fnt_def.scaled_size)
        writer.write_f12d20(fnt_def.design_size)
        a = fnt_def.name.rfind(b"/") + 1
        l = len(fnt_def.name) - a  # noqa: E741
        writer.write_u8(a)
        writer.write_u8(l)
        writer.write_bytes(fnt_def.name)

    def dumps(self) -> str:
        """VPL文字列に変換する。"""
        s = io.StringIO()
        self.dump(s)
        return s.getvalue()

    def dump(self, writer: TextIO):
        """VPLを書き出す。"""
        writer.write(f"(VTITLE {self.comment.decode('ascii')})\n")
        writer.write(f"(CHECKSUM H {self.check_sum:X})\n")
        writer.write(f"(DESIGNSIZE R {to_fixed_str(self.design_size)})\n")

        if self.default_font_num is not None:
            self._dump_map_font(writer, self.default_font_num)
        for fnt_num in sorted(self.font_definitions.keys()):
            if fnt_num != self.default_font_num:
                self._dump_map_font(writer, fnt_num)

        for cc in sorted(self.char_packets.keys()):
            p = self.char_packets[cc]
            writer.write(f"(CHARACTER H {cc:X}\n")
            writer.write(f"   (CHARWD R {to_fixed_str(p.character_width)})\n")
            writer.write("   (MAP\n")
            if isinstance(p.dvi, SimpleDvi):
                if (
                    p.dvi.select_font is not None
                    and p.dvi.select_font != self.default_font_num
                ):
                    writer.write(f"      (SELECTFONT D {p.dvi.select_font})\n")
                if p.dvi.move_right is not None and p.dvi.move_right != 0.0:
                    writer.write(
                        f"      (MOVERIGHT R {to_fixed_str(p.dvi.move_right)})\n"
                    )
                if p.dvi.set_char is not None:
                    writer.write(f"      (SETCHAR H {p.dvi.set_char:X})\n")
            else:
                raise NotImplementedError("Non-simple DVI")
            writer.write("      )\n")
            writer.write("   )\n")

    def _dump_map_font(self, writer: TextIO, fnt_num: int):
        fnt_def = self.font_definitions[fnt_num]
        writer.write(f"(MAPFONT D {fnt_num}\n")
        writer.write(f"   (FONTCHECKSUM H {fnt_def.check_sum:X})\n")
        writer.write(f"   (FONTAT R {to_fixed_str(fnt_def.scaled_size)})\n")
        writer.write(f"   (FONTDSIZE R {to_fixed_str(fnt_def.design_size)})\n")
        writer.write(f"   (FONTNAME {fnt_def.name.decode('ascii')})\n")
        writer.write("   )\n")
