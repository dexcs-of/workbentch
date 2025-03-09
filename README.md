# FreeCAD Macro & WorkBentch for DEXCS Launcher

## これは何か
OpenFOAMを使った仮想風洞試験(注1)を、ボタンを順番に押していくだけで実行できるようにしたDEXCSランチャー（FreeCADのマクロとワークベンチファイル）の一式とセットアップツール。
DEXCS for OpenFOAM で、DEXCS2021より実装されているもので、DEXCS2020に搭載した[DEXCS-FC-Macro](https://gitlab.com/E.Mogura/dexcs-fc-macro)より大幅な変更がある。今後マクロに変更が加えられたら、
変更部分だけを更新しても良いし、同梱のセットアップツールで全体のアップデートも可能。

（注1）デフォルトで仮想風洞試験のパラメタセットになっているというだけで、任意の雛形（OpenFOAMの標準チュートリアルを含む）に変更は可能です。
　　　　
## 注意事項
能書きや、セットアップ方法の記述内容がそのまま通用するかどうかの検証は十分出来ていないので、間違い・不正確な表現や不明点があったらご指摘願いたい。

DEXCSランチャーのうち、DEXCSツールバー中のTreeFoamのサブセット（GridEditorなど）を起動するメニューは、
インストール先の環境によっては動かない場合もある点はお断りしておく。
その場合は面倒ですが、TreeFoamを通常に起動して当該機能を使ってやって下さい。

## 更新 2025/3/9（v0.26）
TreeFoam のSHMツールを起動できるべく、改造・追加
但し、.config/FreeCAD/user.cfg 中の Macro を定義したブロック（<FCParamGroup Name="Macros">）中に、以下の Macro の追加も必要

          <FCParamGroup Name="Std_Macro_18">
            <FCText Name="Script">runTrfSHM.py</FCText>
            <FCText Name="Menu">TrfSHM</FCText>
            <FCText Name="Tooltip">TrfSHMの起動</FCText>
            <FCText Name="WhatsThis">TrfSHMの起動</FCText>
            <FCText Name="Statustip">TrfSHMの起動</FCText>
            <FCText Name="Pixmap">editMesh</FCText>
            <FCText Name="Accel"></FCText>
            <FCBool Name="System" Value="0"/>
          </FCParamGroup>


## 更新 2024/10/11（v0.25）
DEXCS2024用に諸々更新。特にFreeCAD-0.22rev対応。

## 更新 2023/11/7（v0.24）
BugFix: TreeFoamの起動時に、ワークディレクトリが反映されていなかった。根本原因はenvTreeFoamの設定ミスで、これを修正。

## 更新 2023/10/10（v0.23）
dexcsPlotTable.py のボタン追加と、ボタンレイアウトを変更した。

## 更新 2023/9/20（v0.22）
ツールバーの並び順を変更したのと、翻訳辞書周りを整備した。

## 更新 2023/9/8（v0.21）
configDexcsの内容と、Plotツールのデータ数を制限するパラメタ（概略最大データ数と制限方法）をpreferense編集パネルで設定できるようにした。
Plotツールのデータ数制限パラメタは、解析コンテナ毎に個別変更することも可能にした。

## 更新 2023/9/5（v0.2）
Plotモジュールが更新されてimportできなくなった場合に、compat（コンパチ）モジュールをimportするようにした（ハック元CfdOFのやり方を踏襲）。
## 更新 2023/9/3
マクロの登録と呼び出しモジュール（dexcsCfdRditSystemFolder.py など）の不要部削除
## 更新 2023/8/31
FreeCADのワークベンチとしてインストールできるようにすべく、マクロの収納場所やlocaleファイルををワークベンチフォルダ下に移動、併せて移動変更に伴うスクリプト修正を施したもの。
DEXCS2022では、そのまま動くと思うが、その他の環境では、単純に .FreeCAD/Mod/dexcsCfdOFを入れ替えただけでは、（環境によって）動かないかもしれない。
基本的に基本的にuser.cfgを書き換えれば良いはずであるが、書き換え方法を近日公開予定。
