# AnimeHairTools

アニメ風の髪の毛をCurve(Path)で作るのに手数を減らしたい、そんなツールです。

セブンちゃんを作るのに使用しました。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/seven-chan.jpg">

まだインストーラとかないので、普通にスクリプトタブからファイルを取り込んで実行しないと動きません。
プラグインが起動すると、３Dビュー上にAHTというメニューが追加されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/3d-view.jpg">

使い方は、髪の毛用のCurve(Path)を選択して「Create Bone and Hook」ボタンを押してください。自動でArmatureができるのでPoseモードにすれば動くはずです。Curve(Bezier)は未対応です。


## Bevel & Taper Setting

選択中のCurveにBevelとTaperを一括で設定します。

## Create Bone and Hook

最初に座標と回転のコントロール用にボーンを１つ作成し、ターゲットのないConstraintを２つ追加します。スクリプトが完了したらここに顔のボーンを設定してください。

その後選択中のCurveごとにコントロールポイント間の連結Boneが作成され、自動でCurveのPointにHookされます。

最後に選択中のCurveにRotatationのContraintが追加され、ターゲットにコントロール用ボーンを設定します。

## Remove AHT Bone and Hook

選択中のCurveから次のアイテムを削除します
「Create Bone and Hook」で自動生成されたものの削除用。

* Curveの名前から始まるBoneを全て削除する
* Curveの名前から始まるHookを全て削除する
* AHT_rotationという名前のConstraintを削除する
