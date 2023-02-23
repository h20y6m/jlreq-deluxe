jlreq-deluxe パッケージ
=======================

LaTeX：pLaTeX 及び upLaTeX で [jlreq](https://www.ctan.org/pkg/jlreq) クラスを使用する場合に和文を多書体（多ウェイト）にする機能を提供する。

jlreq クラスでは [JLReq](https://www.w3.org/TR/jlreq/?lang=ja) に従った組版を実現するために独自の和文 VF を用いている。このため、多書体（多ウェイト）にしようと [japanese-otf](https://www.ctan.org/pkg/japanese-otf) パッケージを利用すると和文 VF が置き換わってしまい、jlreq クラスの意図する組版が得られなくなってしまう。

このパッケージでは jlreq クラスの提供する和文 VF を元に japanese-otf に合わせた和文 VF を提供し、さらに、[pxjodel](https://www.ctan.org/pkg/pxjodel) パッケージを利用した和文 VF 置き換え機能を提供する。

## 前提条件

* フォーマット：LaTeX
* エンジン：pTeX 及び upTeX
* DVIウェア：和文 VF の fallback 機能をサポートするもの
  - dvipdfmx Version 20200315 以降
  - dvips(k) 2021.1 以降
  - dvisvgm 2.11 以降
* 依存パッケージ：
  - pxjodel パッケージ

## インストール

各ファイルを以下のように配置する。
* `*.sty` -> $TEXMF/tex/platex/jlreq-deluxe/
* `tfm/*.tfm` -> $TEXMF/fonts/tfm/public/jlreq-deluxe
* `vf/*.vf` -> $TEXMF/fonts/vf/public/jlreq-deluxe/

## 使用方法

通常のパッケージと同様に `\usepackage` で読み込む。

```tex
\usepackage[オプション]{jlreq-deluxe}
```

基本的に jlreq クラスとともに使用することを想定しているが、他のクラスでも使用することは出来る。

## オプション

基本的に otf パッケージのと同じオプションが使用できるが、
以下のオプションは動作が異なる。

* `deluxe`
  - 既定で有効になる。
  - 無効にしたい場合は`deluxe=false`を指定する。
* `burasage`
  - 使用できない。
  - ぶら下げ組みを行いたい場合は `hanging_punctuation` オプションを使用する。
* `jis2004`
  - 既定で有効になる。
  - 無効にしたい場合は `jis2004=false` を指定する。
* `uplatex`
  - jlreq クラスを使用している場合は自動的に設定される。
* `scale`
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。

また以下のオプションが使用できる。

* `hanging_punctuation`
  - jlreq クラスの `hanging_punctuation` オプションに対応する VF を使用する。
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。
* `zenkakunibu_nibu`
  - jlreq クラスの `open_bracket_pos=zenkakunibu_nibu` オプションに対応する VF を使用する。
  - jlreq クラスを使用している場合は自動的に設定され指定は無視される。

## ライセンス

このパッケージは [MIT ライセンス](LICENSE)の下で配布される。


更新履歴
-------

* Version 0.4.1 <2023/02/23>
  - e-upTeX ベースの pLaTeX をサポート
* Version 0.4.0 <2021/03/13>
  - 仮想フォントの軽量化
  - ルビ用かなのサポート
* Version 0.3.2 <2021/01/09>
  - `exp*-h.vf` の JIS 0x213C から CID+12364 への引き当てが抜けていたのを修正
* Version 0.3.1 <2020/04/26>
  - ビルドスクリプトの改良
  - テストを追加
  - 英語の README
  - 些細な変更
* Version 0.3.0 <2020/04/14>
  - 独自の和文 VF を作成
  - JIS2004 字形をデフォルトに
  - jlreq クラスではエンジン自動判定
* Version 0.2.0 <2020/03/15>
  - pxjodel 使用版
* Version 0.1.1 <2019/12/21>
  - 和文フォントスケール修正
* Version 0.1.0 <2019/12/01>
  - 初版

-------------------------
Yukimasa Morimi (h20y6m)
https://github.com/h20y6m
