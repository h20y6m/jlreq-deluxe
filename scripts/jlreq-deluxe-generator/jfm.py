from dataclasses import dataclass, field
import io
import logging
from typing import Dict, List, NamedTuple, TextIO

from binaryio import BinaryReader, BinaryWriter
from utils import to_fixed_str, pack_str, unpack_str

logger = logging.getLogger(__name__)


class Glue(NamedTuple):
    natural: float
    stretch: float = 0.0
    shrink: float = 0.0


@dataclass
class CharInfo:
    width: float = 0.0
    height: float = 0.0
    depth: float = 0.0
    italic: float = 0.0
    glue_kern: Dict[int, Glue | float] = field(default_factory=dict)


YOKO_ID = 11
TATE_ID = 9


class BadJFM(Exception):
    pass


class JFM:
    def __init__(self):
        self.id: int = YOKO_ID
        self.check_sum: int = 0
        self.design_size: float = 10.0
        self.coding_scheme: bytes = b"UNSPECIFIED"
        self.family: bytes = b"UNSPECIFIED"
        self.face: int = 0

        self.chars_type: Dict[int, int] = {}
        self.char_info: List[CharInfo] = []

        self.slant: float = 0.0
        self.kanjiskip: Glue = Glue(0.0, 0.0, 0.0)
        self.zh: float = 10.0
        self.zw: float = 10.0
        self.xkanjiskip: Glue = Glue(0.0, 0.0, 0.0)

    def get_char_type(self, cc: int) -> int:
        return self.chars_type[cc] if cc in self.chars_type else 0

    def get_type_width(self, char_type: int) -> float:
        return self.char_info[char_type].width

    def get_char_width(self, cc: int) -> float:
        char_type = self.get_char_type(cc)
        return self.get_type_width(char_type)

    def load(self, file):
        with BinaryReader(file) as reader:
            self.id = reader.read_i16()
            logger.debug(f"id={id}")
            if self.id != YOKO_ID and self.id != TATE_ID:
                raise BadJFM("File is not a JFM file")

            nt = reader.read_i16()
            lf = reader.read_i16()
            lh = reader.read_i16()
            bc = reader.read_i16()
            ec = reader.read_i16()
            nw = reader.read_i16()
            nh = reader.read_i16()
            nd = reader.read_i16()
            ni = reader.read_i16()
            nl = reader.read_i16()
            nk = reader.read_i16()
            ng = reader.read_i16()
            np = reader.read_i16()
            logger.debug(f"nt={nt}")
            logger.debug(f"lf={lf}")
            logger.debug(f"lh={lh}")
            logger.debug(f"bc={bc}")
            logger.debug(f"ec={ec}")
            logger.debug(f"nw={nw}")
            logger.debug(f"nh={nh}")
            logger.debug(f"nd={nd}")
            logger.debug(f"ni={ni}")
            logger.debug(f"nl={nl}")
            logger.debug(f"nk={nk}")
            logger.debug(f"ng={ng}")
            logger.debug(f"np={np}")
            if nt < 0:
                raise BadJFM("Bad 'nt' value")
            if (
                lf < 0
                or lf
                != 7 + lh + nt + (ec - bc + 1) + nw + nh + nd + ni + nl + nk + ng + np
            ):
                raise BadJFM("Bad 'lf' value")
            if lh < 0:
                raise BadJFM("Bad 'lh' value")
            if bc != 0:
                raise BadJFM("Bad 'bc' value")
            if ec < 0 or ec >= 256:
                raise BadJFM("Bad 'ec' value")
            if nw < 0:
                raise BadJFM("Bad 'nw' value")
            if nh < 0:
                raise BadJFM("Bad 'nh' value")
            if nd < 0:
                raise BadJFM("Bad 'nd' value")
            if ni < 0:
                raise BadJFM("Bad 'ni' value")
            if nl < 0:
                raise BadJFM("Bad 'nl' value")
            if nk < 0:
                raise BadJFM("Bad 'nk' value")
            if ng < 0:
                raise BadJFM("Bad 'ng' value")
            if np < 0:
                raise BadJFM("Bad 'np' value")

            # header
            if lh < 2:
                raise BadJFM("too small header")
            self.check_sum = reader.read_u32()
            self.design_size = reader.read_f12d20()
            logger.debug(f"check_sum={self.check_sum}")
            logger.debug(f"design_size={self.design_size}")
            if lh > 2:
                if lh <= 11:
                    raise BadJFM("too small header")
                self.coding_scheme = unpack_str(reader.read_bytes(40))
                logger.debug(f"coding_scheme={self.coding_scheme}")
            if lh > 11:
                if lh <= 16:
                    raise BadJFM("too small header")
                self.family = unpack_str(reader.read_bytes(20))
                logger.debug(f"family={self.family}")
            if lh > 16:
                v = reader.read_bytes(4)
                self.face = v[3]
                logger.debug(f"face={self.face}")
            if lh > 17:
                for i in range(18, lh):
                    v = reader.read_u32()
                    logger.debug(f"header[{i}]={v}")

            # char_type
            if reader.read_u32() != 0:
                raise BadJFM("Bad 'char_type' table.")
            self.chars_type = {}
            last_k = 0
            for i in range(nt - 1):
                k = reader.read_u16()
                t = reader.read_u16()
                k += (t >> 8) << 16
                t = t & 0xFF
                logger.debug(f"chars_type[{k}]={t}")
                if k < last_k:
                    logger.warning("The 'char_type' table is not sorted by KANJI code.")
                last_k = k
                if t > ec:
                    raise BadJFM("Bad 'char_type'.")
                if t == 0:
                    continue
                self.chars_type[k] = t

            # char_info
            char_info = []
            for i in range(ec + 1):
                b = reader.read_bytes(4)
                width_index = b[0]
                height_index = b[1] >> 4
                depth_index = b[1] & 0x0F
                italic_index = b[2] >> 2
                tag = b[2] & 0x03
                remainder = b[3]
                logger.debug(
                    f"char_info[{i}]={(width_index, height_index, depth_index, italic_index, tag, remainder)}"
                )
                if width_index >= nw:
                    raise BadJFM("Bad 'width_index'.")
                if height_index >= nh:
                    raise BadJFM("Bad 'height_index'.")
                if depth_index >= nd:
                    raise BadJFM("Bad 'depth_index'.")
                if italic_index >= ni:
                    raise BadJFM("Bad 'italic_index'.")
                if tag >= 2:
                    raise BadJFM("Bad 'tag'.")
                if tag == 1 and remainder >= nl:
                    raise BadJFM("Bad glue/kern index.")
                char_info.append(
                    (
                        width_index,
                        height_index,
                        depth_index,
                        italic_index,
                        tag,
                        remainder,
                    )
                )

            # width
            width_table = []
            for i in range(nw):
                width = reader.read_f12d20()
                logger.debug(f"width[{i}]={width}")
                width_table.append(width)

            # height
            height_table = []
            for i in range(nh):
                height = reader.read_f12d20()
                logger.debug(f"height[{i}]={height}")
                height_table.append(height)

            # depth
            depth_table = []
            for i in range(nd):
                depth = reader.read_f12d20()
                logger.debug(f"depth[{i}]={depth}")
                depth_table.append(depth)

            # italic
            italic_table = []
            for i in range(ni):
                italic = reader.read_f12d20()
                logger.debug(f"italic[{i}]={italic}")
                italic_table.append(italic)

            # glue/kern program
            glue_kern_table = []
            for i in range(nl):
                b = reader.read_bytes(4)
                skip_byte = b[0]
                char_type = b[1]
                op_byte = b[2]
                remainder = b[3]
                logger.debug(
                    f"glue_kern[{i}]={(skip_byte, char_type, op_byte, remainder)}"
                )
                if char_type > ec:
                    raise BadJFM("Bad 'char_type' in glue/kern program.")
                if op_byte < 128:
                    if remainder * 3 >= ng:
                        raise BadJFM("Bad glue index.")
                else:
                    if remainder >= nk:
                        raise BadJFM("Bad kern index.")
                glue_kern_table.append((skip_byte, char_type, op_byte, remainder))

            # kern table
            kern_table = []
            for i in range(nk):
                kern = reader.read_f12d20()
                logger.debug(f"kern[{i}]={kern}")
                kern_table.append(kern)

            # glue table
            glue_table = []
            for i in range(ng // 3):
                glue_natural = reader.read_f12d20()
                glue_stretch = reader.read_f12d20()
                glue_shrink = reader.read_f12d20()
                glue = Glue(glue_natural, glue_stretch, glue_shrink)
                logger.debug(f"glue[{i}]={glue}")
                glue_table.append(glue)

            #
            self.char_info = []
            for i, info in enumerate(char_info):
                width_index, height_index, depth_index, italic_index, tag, remainder = (
                    info
                )
                width = width_table[width_index]
                height = height_table[height_index]
                depth = depth_table[depth_index]
                italic = italic_table[italic_index]
                glue_kern = {}
                if tag == 1:
                    glue_kern_index = remainder
                    while glue_kern_index < nl:
                        skip_byte, char_type, op_byte, remainder = glue_kern_table[
                            glue_kern_index
                        ]
                        if char_type in glue_kern:
                            logger.warning(
                                f"Duplicate 'char_type' {char_type} in glue/kern program for {i}."
                            )
                        elif op_byte < 128:
                            # GLUE
                            glue_kern[char_type] = glue_table[remainder]
                        else:
                            # KRN
                            glue_kern[char_type] = kern_table[remainder]
                        if skip_byte >= 128:
                            # STOP
                            break
                        if skip_byte > 0:
                            # SKIP
                            raise NotImplementedError(
                                "Non-zero 'skip_byte' not supported (yet)."
                            )
                        glue_kern_index += 1
                self.char_info.append(CharInfo(width, height, depth, italic, glue_kern))

            # param
            param = [0.0 for _ in range(max(np, 9))]
            for i in range(np):
                param[i] = reader.read_f12d20()
                logger.debug(f"param[{i}]={param[i]}")
            self.slant = param[0]
            self.kanjiskip = Glue(param[1], param[2], param[3])
            self.zh = param[4]
            self.zw = param[5]
            self.xkanjiskip = Glue(param[6], param[7], param[8])

    def save(self, file):
        """Save JFM file."""
        # Remove char_type == 0
        self.chars_type = {k: t for k, t in self.chars_type.items() if t != 0}

        char_info_table = []
        width_table = [0.0]
        height_table = [0.0]
        depth_table = [0.0]
        italic_table = [0.0]
        gluekern_table = []
        kern_table = []
        glue_table: List[Glue] = []
        for i, info in enumerate(self.char_info):
            # width_index == 0 indicates no characters, so do not use it
            if info.width not in width_table[1:]:
                width_index = len(width_table)
                if width_index >= 256:
                    raise BadJFM("Too many distinct values for 'width'.")
                width_table.append(info.width)
            else:
                width_index = width_table[1:].index(info.width) + 1

            if info.height not in height_table:
                height_index = len(height_table)
                if height_index >= 16:
                    raise BadJFM("Too many distinct values for 'height'.")
                height_table.append(info.height)
            else:
                height_index = height_table.index(info.height)

            if info.depth not in depth_table:
                depth_index = len(depth_table)
                if depth_index >= 16:
                    raise BadJFM("Too many distinct values for 'depth'.")
                depth_table.append(info.depth)
            else:
                depth_index = depth_table.index(info.depth)

            if info.italic not in italic_table:
                italic_index = len(italic_table)
                if italic_index >= 64:
                    raise BadJFM("Too many distinct values for 'italic'.")
                italic_table.append(info.italic)
            else:
                italic_index = italic_table.index(info.italic)

            char_info_tag = 0
            char_info_remainder = 0
            program = []
            for j in sorted(info.glue_kern.keys()):
                glue_or_kern = info.glue_kern[j]
                if isinstance(glue_or_kern, Glue):
                    if glue_or_kern not in glue_table:
                        glue_table.append(glue_or_kern)
                    glue_index = glue_table.index(glue_or_kern)
                    program.append((0, j, 0, glue_index))
                else:  # KRN
                    if glue_or_kern not in kern_table:
                        kern_table.append(glue_or_kern)
                    kern_index = kern_table.index(glue_or_kern)
                    program.append((0, j, 128, kern_index))
            if len(program) > 0:
                program[-1] = (128, program[-1][1], program[-1][2], program[-1][3])
                gluekern_index = -1
                for j in range(len(gluekern_table) - len(program) + 1):
                    if gluekern_table[j : j + len(program)] == program:
                        logger.debug(f"Match glue/kern for char_type {i} at {j}.")
                        gluekern_index = j
                        break
                if gluekern_index < 0:
                    gluekern_index = len(gluekern_table)
                    gluekern_table += program
                    logger.debug(
                        f"Add glue/kern for char_type {i} at {gluekern_index}."
                    )
                    # logger.debug(f"{program}")
                char_info_tag = 1
                char_info_remainder = gluekern_index

            char_info_table.append(
                (
                    width_index,
                    height_index,
                    depth_index,
                    italic_index,
                    char_info_tag,
                    char_info_remainder,
                )
            )

        nt = 1 + len(self.chars_type)
        lf = 0
        lh = 18
        bc = 0
        ec = max(0, *self.chars_type.values())
        nw = len(width_table)
        nh = len(height_table)
        nd = len(depth_table)
        ni = len(italic_table)
        nl = len(gluekern_table)
        nk = len(kern_table)
        ng = 3 * len(glue_table)
        np = 9

        lf = 7 + lh + nt + (ec - bc + 1) + nw + nh + nd + ni + nl + nk + ng + np

        with BinaryWriter(file) as writer:
            writer.write_u16(self.id)

            writer.write_u16(nt)
            writer.write_u16(lf)
            writer.write_u16(lh)
            writer.write_u16(bc)
            writer.write_u16(ec)
            writer.write_u16(nw)
            writer.write_u16(nh)
            writer.write_u16(nd)
            writer.write_u16(ni)
            writer.write_u16(nl)
            writer.write_u16(nk)
            writer.write_u16(ng)
            writer.write_u16(np)

            writer.write_u32(self.check_sum)
            writer.write_f12d20(self.design_size)
            writer.write_bytes(pack_str(40, self.coding_scheme))
            writer.write_bytes(pack_str(20, self.family))
            writer.write_bytes(bytes([0x80, 0, 0, self.face]))

            writer.write_u32(0)
            for k in sorted(self.chars_type.keys()):
                t = self.chars_type[k]
                writer.write_u16(k & 0xFFFF)
                writer.write_u16(t | ((k >> 16) << 8))

            for char_info in char_info_table:
                (
                    width_index,
                    height_index,
                    depth_index,
                    italic_index,
                    char_info_tag,
                    char_info_remainder,
                ) = char_info
                writer.write_u8(width_index)
                writer.write_u8((height_index << 4) | depth_index)
                writer.write_u8((italic_index << 2) | char_info_tag)
                writer.write_u8(char_info_remainder)

            for width in width_table:
                writer.write_f12d20(width)

            for height in height_table:
                writer.write_f12d20(height)

            for depth in depth_table:
                writer.write_f12d20(depth)

            for italic in italic_table:
                writer.write_f12d20(italic)

            for glue_kern in gluekern_table:
                skip_byte, char_type, op_byte, remainder = glue_kern
                writer.write_u8(skip_byte)
                writer.write_u8(char_type)
                writer.write_u8(op_byte)
                writer.write_u8(remainder)

            for kern in kern_table:
                writer.write_f12d20(kern)

            for glue in glue_table:
                writer.write_f12d20(glue.natural)
                writer.write_f12d20(glue.stretch)
                writer.write_f12d20(glue.shrink)

            writer.write_f12d20(self.slant)
            writer.write_f12d20(self.kanjiskip.natural)
            writer.write_f12d20(self.kanjiskip.stretch)
            writer.write_f12d20(self.kanjiskip.shrink)
            writer.write_f12d20(self.zh)
            writer.write_f12d20(self.zw)
            writer.write_f12d20(self.xkanjiskip.natural)
            writer.write_f12d20(self.xkanjiskip.stretch)
            writer.write_f12d20(self.xkanjiskip.shrink)

    def dumps(self):
        writer = io.StringIO()
        self.dump(writer)
        return writer.getvalue()

    def dump(self, writer: TextIO):
        if self.id == YOKO_ID:
            writer.write("(DIRECTION YOKO)\n")
        elif self.id == TATE_ID:
            writer.write("(DIRECTION TATE)\n")

        writer.write(f"(CHECKSUM H {self.check_sum:X})\n")
        writer.write(f"(DESIGNSIZE R {to_fixed_str(self.design_size)})\n")
        writer.write(f"(CODINGSCHEME {self.coding_scheme.decode('ascii')})\n")
        writer.write(f"(FAMILY {self.family.decode('ascii')})\n")
        if self.face < 18:
            writer.write("(FACE F ")
            writer.write(["M", "B", "L"][self.face % 6 // 2])
            writer.write(["R", "I"][self.face % 2])
            writer.write(["R", "C", "E"][self.face % 18 // 6])
            writer.write(")\n")
        else:
            writer.write(f"(FACE D {self.face})")

        chars_in_type = {}
        not_jis = False
        for k, t in self.chars_type.items():
            if t not in chars_in_type:
                chars_in_type[t] = []
            chars_in_type[t].append(k)
            if k < 0x2121 or k > 0x7E7E:
                not_jis = True
            else:
                k1 = k >> 8
                k2 = k & 0xFF
                if k1 < 0x21 or k1 > 0x7E or k2 < 0x21 or k2 > 0x7E:
                    not_jis = True
        for t in sorted(chars_in_type.keys()):
            chars_in_type[t].sort()
            writer.write(f"(CHARSINTYPE D {t}")
            for i, k in enumerate(chars_in_type[t]):
                if i % 10 == 0:
                    writer.write("\n  ")
                if not_jis:
                    writer.write(f" U {k:04X}")
                else:
                    writer.write(f" J {k:04X}")
            writer.write("\n   )\n")

        for t, info in enumerate(self.char_info):
            writer.write(f"(TYPE D {t}\n")
            if info.width != 0:
                writer.write(f"   (CHARWD R {to_fixed_str(info.width)})\n")
            if info.height != 0:
                writer.write(f"   (CHARHT R {to_fixed_str(info.height)})\n")
            if info.depth != 0:
                writer.write(f"   (CHARDP R {to_fixed_str(info.depth)})\n")
            if info.italic != 0:
                writer.write(f"   (CHARIC R {to_fixed_str(info.italic)})\n")
            writer.write("   )\n")

        writer.write("(GLUEKERN\n")
        glue_kern_label = {}
        for t, info in enumerate(self.char_info):
            if t in glue_kern_label:
                continue
            writer.write(f"   (LABEL D {t})\n")
            for t2, info2 in enumerate(self.char_info):
                if t2 > t and info.glue_kern == info2.glue_kern:
                    writer.write(f"   (LABEL D {t2})\n")
                    glue_kern_label[t2] = t
            for t2 in sorted(info.glue_kern.keys()):
                glue_or_kern = info.glue_kern[t2]
                if isinstance(glue_or_kern, Glue):
                    writer.write(
                        f"   (GLUE D {t2} R {to_fixed_str(glue_or_kern.natural)} R {to_fixed_str(glue_or_kern.stretch)} R {to_fixed_str(glue_or_kern.shrink)})\n"
                    )
                else:  # KRN
                    writer.write(f"   (KRN D {t2} R {to_fixed_str(glue_or_kern)})\n")
            writer.write("   (STOP)\n")
        writer.write("   )\n")

        writer.write("(FONTDIMEN\n")
        writer.write(f"   (SLANT R {to_fixed_str(self.slant)})\n")
        writer.write(f"   (SPACE R {to_fixed_str(self.kanjiskip.natural)})\n")
        writer.write(f"   (STRETCH R {to_fixed_str(self.kanjiskip.stretch)})\n")
        writer.write(f"   (SHRINK R {to_fixed_str(self.kanjiskip.shrink)})\n")
        writer.write(f"   (XHEIGHT R {to_fixed_str(self.zh)})\n")
        writer.write(f"   (QUAD R {to_fixed_str(self.zw)})\n")
        writer.write(f"   (EXTRASPACE R {to_fixed_str(self.xkanjiskip.natural)})\n")
        writer.write(f"   (EXTRASTRETCH R {to_fixed_str(self.xkanjiskip.stretch)})\n")
        writer.write(f"   (EXTRASHRINK R {to_fixed_str(self.xkanjiskip.shrink)})\n")
        writer.write("   )\n")

    def _build_glue_kern(self):
        pass
        glue_kern_table = []
        for t1, info1 in enumerate(self.char_info):
            info1_glue_kern = info1.glue_kern
            if info1_glue_kern is not None:
                glue_kern_items = []
                for t2, glue_kern_item in enumerate(info1_glue_kern):
                    if glue_kern_item is not None:
                        glue_kern_items.append((t2, glue_kern_item))
                glue_kern_table.append((t1, glue_kern_items))
        for i in range(len(glue_kern_table)):
            for j in range(i + 1, len(glue_kern_table)):
                t1, gk1 = glue_kern_table[i]
                t2, gk2 = glue_kern_table[j]
                if len(gk1) < len(gk2):
                    k = len(gk2) - len(gk1)
                    if gk1 == gk2[k:]:
                        t = glue_kern_table[i]
                        glue_kern_table[j] = glue_kern_table[i]
                        glue_kern_table[i] = t
