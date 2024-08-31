# FreeCAD WorkBentch for DEXCS Launcher

## これは何か
OpenFOAMを使った仮想風洞試験(注1)を、ボタンを順番に押していくだけで実行できるようにしたDEXCSランチャー（FreeCADのマクロとワークベンチファイル）一式。
DEXCS for OpenFOAM で、DEXCS2021より実装されているもので、DEXCS2020に搭載した[DEXCS-FC-Macro](https://gitlab.com/E.Mogura/dexcs-fc-macro)や、DEXCS2022用の[dexcs-of/launcher](https://github.com/dexcs-of/launcher)より大幅な変更がある。DEXCS2023以降、FreeCADの設定ファイルの置き場所に関して仕様が変更されたので、本レポジトリにて公開することとした。

（注1）デフォルトで仮想風洞試験のパラメタセットになっているというだけで、任意の雛形（OpenFOAMの標準チュートリアルを含む）に変更は可能です。

## インストール方法

$HOME/.local/share/FreeCAD/Mod/dexcsCfdOF の内容をそのまま置き換えれば良い 。
　　　　
## 注意事項
能書きや、インストール方法の記述内容がそのまま通用するかどうかの検証は十分出来ていないので、間違い・不正確な表現や不明点があったらご指摘願いたい。

DEXCSランチャーのうち、DEXCSツールバー中のTreeFoamのサブセット（GridEditorなど）を起動するメニューは、
インストール先の環境によっては動かない場合もある点はお断りしておく（DEXCS2023）。
その場合は面倒ですが、TreeFoamを通常に起動して当該機能を使ってやって下さい。

