# FreeCAD Macro & WorkBentch for DEXCS Launcher
# 更新 2022/6/13
DEXCS2022 の正式公開に向けて、諸々改定版を暫定公開

改定内容は、
 https://ocse2.com/?p=13966
 
の記事を参照されたい。

## これは何か
OpenFOAMを使った仮想風洞試験(注1)を、ボタンを順番に押していくだけで実行できるようにしたDEXCSランチャー（FreeCADのマクロとワークベンチファイル）の一式とセットアップツール。
DEXCS for OpenFOAM で、DEXCS2021より実装されているもので、DEXCS2020に搭載した[DEXCS-FC-Macro](https://gitlab.com/E.Mogura/dexcs-fc-macro)より大幅な変更がある。今後マクロに変更が加えられたら、
変更部分だけを更新しても良いし、同梱のセットアップツールで全体のアップデートも可能。

（注1）デフォルトで仮想風洞試験のパラメタセットになっているというだけで、任意の雛形に変更は可能です。
　　　　
## 注意事項
能書きや、セットアップ方法の記述内容がそのまま通用するかどうかの検証は十分出来ていないので、間違い・不正確な表現や不明点があったらご指摘願いたい。

DEXCSランチャーのうち、DEXCSツールバー中のTreeFoamのサブセット（GridEditorなど）を起動するメニューは、
インストール先の環境によっては動かない場合もある点はお断りしておく。
その場合は面倒ですが、TreeFoamを通常に起動して当該機能を使ってやって下さい。

## セットアップ方法

同梱のconfigDexcs というファイル中で定義してある3つのパラメタ(cfMesh, TreeFoam, dexcs)の内容(行頭に # の有る行はコメント行)を、
インストール先の環境に合致させておいてから（注2）、同梱の updateDexcsLauncher.sh を端末上で実行する。
その際、既存の user.cfg を上書きするかどうかの質問があるので、上書きして良ければ「 Y 」を入力してアップデートは完了。

上書きの可否は、インストール先の FreeCAD の利用環境で自身でカスタマイズしたマクロやツールバーの有無次第で判断されたい。
上書きしてしまうと、それらの情報が無くなってしまうということである。「 N 」を入力した場合には、
マクロファイルがアップデートされるだけなので、ツールボタンを自身で作り直す作業が必要になる。作り直す方法については、

https://ocse2.com/?p=12722

の記事を参照されたい。


なお、上書きした場合でも、元の user.cfg ファイルは、 user.cfg.\<user\>.orig という名前（\<user\>の部分はユーザー名）で残すようにしてあるので復元は可能。
またテキストファイルなので、内容を理解した上での新旧ファイル間での組み合わせ改変は可能である。

（注2）旧版DEXCS用には拡張子で区別出来るようにしてあるので、その拡張子を外して使えば良い。例：DEXCS2019 の場合は、configDexcs.2019 を configDexcsに変更

## FreeCADの更新

DEXCS2019以前では、FreeCADを最新のAppImage版（FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage）に更新する必要がある。
更新方法はダウンロードしたAppImage版の収納されたフォルダにて、
管理者権限にて、たとえば以下のコマンドを入力すれば良い。
```
	chmod +x FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage
	cp FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage /opt/
	ln -s /opt/FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage /opt/freecad 
	mv /usr/bin/freecad /usr/bin/freecad.orig
	ln -s /opt/freecad /usr/bin/freecad
	mv /usr/bin/freecad-daily /usr/bin/freecad-daily.orig
	ln -s /opt/freecad /usr/bin/freecad-daily
```
元々インストールされてあった/usr/bin/freecad なり、/usr/bin/freecad-dailyは、.orig の拡張子を付けて残すようにしてあるので、戻したい場合はこれを使えば良い。 

## FreeCADの設定
FreeCADの「編集」⇒「設定」メニューの「dexcsCfdOf」で、OpenFOAMのインストールパスとParaViewの実行プログラム名、テンプレートケースの指定が必要。
テンプレートケースの中身は、OpenFOAMのケースファイルとして有効な内容であれば何でも良いが、 FreeCAD モデルが OpenFOAM のケースファイルでない場
所でメッシュ作成する際の雛形フォルダとして使われることになる。

## 動作を確認できているDEXCS for OpenFOAM

* DEXCS2021
* DEXCS2020
* DEXCS2019
* DEXCS2018
* DEXCS2017
* DEXCS2016
* DEXCS2015
（但し、DEXCS2019以前では、DEXCSツールバー中、TreeFoamのサブセット機能は使えないものがある）

## DEXCS 以外のプラットフォームで動作させる為の要件
FreeCADは最新のAppImage版（FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage）に更新することを推奨する（それ以外での検証は未実施）。

DEXCS for OpenFOAM で構築したシステムでなくとも、
OpenFOAM（含むcfMesh）とParaViewが動く環境であればDEXCSワークベンチは動作するはずである。
また TreeFoam が動く環境であれば、DEXCSツールバーも含めて動作するはずなので、その要件と追加方法について記しておく。
（但し、実際に動作確認している訳ではないので、不具合があればレポートをお願いします）
CentOS7上で動作確認した以下の記事も参照されたい。

https://ocse2.com/?p=13506

* cfMesh ( cartesianMesh )がインストールされており、 configDecs 中に、これを起動する為の(ビルドした)
OpenFOAM の環境情報が記してある事。
* TreeFoam がインストールされていない場合には、DEXCSツールバーから起動するTreeFoamのサブセット機能が使えないというだけで、DEXCSワークベンチは使用可能。
* TreeFoam がインストールされている場合( +dexcsSwak 版でなくとも可)、 configDecs 中に configTreeFoam のイ
ンストール場所が記されている事。
	* configDecs 中に dexcs 指定フォルダを定義しておき、指定したフォルダ下に SWAK というフォルダと template
というフォルダを作成。 SWAK フォルダ下に pyDexcsSwak.py という空ファイルを作成。



