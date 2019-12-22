# AnimeHairTools

アニメ風の髪の毛をCurve(Path)で作るのに手数を減らしたい、そんなツールです。

セブンちゃんを作るのに使用しました。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/seven-chan.jpg">

Editboxの出し方がわからなかったので、ShepeKeyの値はとりあえず選択(+Valueを1.0に)と、リセット(Valueを0.0に)を用意してしのぎました。
出し方が分かったらShapeKeyの名前とValueの値を設定できるようにしたいところです。

まだインストーラとかないので、普通にスクリプトタブからファイルを取り込んで実行しないと動きません。
プラグインが起動すると、３Dビュー上にAHTというメニューが追加されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/3d-view.jpg">


## Bevel & Taper Setting

選択中のCurveにBevelとTaperを一括で設定する。

## Create Bone and Hook

最初に座標と回転のコントロール用にボーンを１つ作成し、ターゲットのないConstraintを２つ追加します。スクリプトが完了したらここに顔のボーンを設定してください。

その後Curveごとにコントロールポイント間の連結Boneが作成され、自動でCurveのPointにHookされます。

最後に選択中のCurveにRotatationのContraintが追加され、ターゲットにコントロール用ボーンを設定します。

## Remove AHT Bone and Hook

選択中のCurveから次のアイテムを削除します
「Create Bone and Hook」で自動生成されたものの削除用。

* Curveの名前から始まるBoneを全て削除する
* Curveの名前から始まるHookを全て削除する
* AHT_rotationという名前のConstraintを削除する
