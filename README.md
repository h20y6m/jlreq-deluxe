jlreq-deluxe Package
====================

LaTeX: Multi-weight Japanese font support for jlreq class.

## System requirement

* TeX format: LaTeX.
* TeX engine: pTeX and upTeX.
* DVI drivers: Anything that Support feature of virtual font to fallback Japanese font definition.
  - dvipdfmx Version 20200315 or later.
  - dvips(k) 2021.1 or later.
  - dvisvgm 2.11 or later.
* Dependent packages:
  - pxjodel

## Installation

* `*.sty` -> $TEXMF/tex/platex/jlreq-deluxe/
* `tfm/*.tfm` -> $TEXMF/fonts/tfm/public/jlreq-deluxe/
* `vf/*.vf` -> $TEXMF/fonts/vf/public/jlreq-deluxe/

## Usage

See [README-ja.md](README-ja.md) (in Japanese).

## License

This package is distributed under [the MIT License](LICENSE).


History
-------

* Version 0.4.1 <2023/02/23>
  - Support e-upTeX based pLaTeX.
* Version 0.4.0 <2021/03/13>
  - Compact virtual fonts.
  - Add support for the ruby family.
* Version 0.3.2 <2021/01/09>
  - Fix missing map JIS 0x213C to CID+12364 in exp*-h.vf.
* Version 0.3.1 <2020/04/26>
  - Improve build script.
  - Add test.
  - Add english README.
  - Small fix.
* Version 0.3.0 <2020/04/14>
  - Use custom VF/JFM.
  - JIS2004 glyph as default.
  - Auto-detect engine in jlreq class.
* Version 0.2.0 <2020/03/15>
  - Use pxjodel package.
* Version 0.1.1 <2019/12/21>
  - Fix Japanese font scale.
* Version 0.1.0 <2019/12/01>
  - The first version.

-------------------------
Yukimasa Morimi (h20y6m)
https://github.com/h20y6m
