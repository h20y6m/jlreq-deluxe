jlreq-deluxe パッケージ
=======================

LaTeX：八登崇之氏作成の [pxjodel](https://www.ctan.org/pkg/pxjodel) パッケージを利用し pLaTeX 及び upLaTeX で jlreq クラスを使用する場合に和文を多書体（多ウェイト）にする。

## 前提条件

* フォーマット：LaTeX
* エンジン：pTeX 及び upTeX
* DVIウェア：和文 TFM と VF をサポートするもの。
* 依存パッケージ
  - [jlreq](https://www.ctan.org/pkg/jlreq) クラス
  - pxjodel パッケージ

## インストール

以下のコマンドで必要なファイルを生成する。
```
l3build makejvf
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

通常のパッケージと同様に `\usepackage` で読み込む。

```tex
\usepackage[オプション]{jlreq-deluxe}
```

基本的に jlreq クラスとともに使用することを想定しているが、
他のクラスでも使用することは出来る。

\section{オプション}

基本的に otf パッケージのと同じオプションが使用できるが、
以下のオプションは動作が異なる。

* `deluxe`
  - 既定で有効になる。
  - 無効にしたい場合は|deluxe=false|を指定する。
* `expert`
  - 使用できない。
* `burasage`
  - 使用できない。
* `scale`
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。

また以下のオプションが使用できる。

* `hanging_punctuation`
  - jlreq クラスの `hanging_punctuation` 指定時用のJFMを使用する。
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。
* `zenkakunibu_nibu`
  - jlreq クラスの `open_bracket_pos=zenkakunibu_nibu` 指定時用のJFMを使用する。
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。


更新履歴
-------

* Version 0.2.0 <2020/03/15>
  - pxjodel 使用版
* Version 0.1.1 <2019/12/21>
  - 和文フォントスケール修正
* Version 0.1.0 <2019/12/01>
  - 初版

------
h20y6m
https://github.com/h20y6m
