jlreq-deluxe パッケージ
=======================

LaTeX：pLaTeX 及び upLaTeX で jlreq クラスを使用する場合に和文を多書体（多ウェイト）にする。

## 前提条件

* フォーマット：LaTeX
* エンジン：pTeX 及び upTeX
* DVIウェア：dvipdfmx
* 依存パッケージ
  - jlreq クラス
  - otf パッケージ

## インストール

以下のコマンドで必要なファイルを生成する。
```
l3build vfcopy
```

各ファイルを以下のように配置する。
* *.sty -> $TEXMF/tex/platex/jlreq-deluxe
* *.tfm -> $TEXMF/fonts/tfm/public/jlreq-deluxe
* *.vf -> $TEXMF/fonts/vf/public/jlreq-deluxe

もしくは
```
l3build install
```
とすると `TEXMFHOME` にインストールされる。

## 使用方法

```tex
\usepakage{jlreq-deluxe}
```
とする。以下のフォントが使用可能になる。
* 明朝・細ウェイト（`\mcfamily\ltseries`）
* 明朝・中ウェイト（`\mcfamily\mdseries`）
* 明朝・太ウェイト（`\mcfamily\bfseries`）
* ゴシック・中ウェイト（`\gtfamily\mdseries`）
* ゴシック・太ウェイト（`\gtfamily\bfseries`）
* ゴシック・極太ウェイト（`\gtfamily\ebseries`）
* 丸ゴシック（`\mgfamily`）

### フォント指定

以下のフォント指定命令が使用できる。
* `\setminchofont[<index>]{<fontfile>}`
  - 明朝体 3 ウェイトのフォントをすべて `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setlightminchofont[<index>]{<fontfile>}`
  - 明朝体・細ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setmediumminchofont[<index>]{<fontfile>}`
  - 明朝体・中ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setboldminchofont[<index>]{<fontfile>}`
  - 明朝体・太ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setgothicfont[<index>]{<fontfile>}`
  - ゴシック体 3 ウェイトのフォントをすべて `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setmediumgothicfont[<index>]{<fontfile>}`
  - ゴシック体・細ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setboldgothicfont[<index>]{<fontfile>}`
  - ゴシック体・中ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setxboldgothicfont[<index>]{<fontfile>}`
  - ゴシック体・太ウェイトのフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。
* `\setmarugothicfont[<index>]{<fontfile>}`
  - 丸ゴシック体のフォントを `<fontfile>` にする。
    `<index>` は TTC インデックス。

### フォントプリセット

パッケージ読み込み時にフォントプリセットを指定できる。
```tex
\usepackage[<preset>]{jlreq-deluxe}
```

使用可能なプリセットは
`ms`、`ipa`、`ipaex`、
`ms-hg`、`ipa-hg`、`ipaex-hg`、
`moga-mobo`、`moga-mobo-ex`、`moga-maruberi`、
`ume`、
`kozuka-pro`、`kozuka-pr6`、`kozuka-pr6n`、
`hiragino-pro`、`hiragino-pron`、`hiragino-elcapitan-pro`、`hiragino-elcapitan-pron`、
`morisawa-pro`、`morisawa-pr6n`、
`yu-win`、`yu-win10`、`yu-osx`、
`sourcehan-otc`、`sourcehan`、`sourcehan-jp`、
`noto-otc`、`noto`、`noto-jp`、
`haranoaji`。

ただし `sourcehan-otc`、`sourcehan`、`sourcehan-jp`、
`noto-otc`、`noto`、`noto-jp` は pLaTeX では使用できない。

更新履歴
-------

* Version 0.1.0 <2019/12/01>
  - 初版

------
h20y6m
https://github.com/h20y6m
