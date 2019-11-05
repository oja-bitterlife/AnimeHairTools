# AnimeHairTools

アニメ風の髪の毛をCurve(Path)で作るのに手数を減らしたい、そんなツールです。

セブンちゃんを作るのに使用しました。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/seven-chan.jpg">

Editboxの出し方がわからなかったので、ShepeKeyの値はとりあえず選択(+Valueを1.0に)と、リセット(Valueを0.0に)を用意してしのぎました。
出し方が分かったらShapeKeyの名前とValueの値を設定できるようにしたいところです。

## Bevel & Taper Setting

選択中のCurveにBevelとTaperを一括で設定する。

## Material Setting

選択中のCurveのMaterialを一括で変更する。

マテリアルがすでにSlotにあればそれを使う。SlotになければSlotを追加してそこにマテリアルを設定して使う。

## Create Bone and Constraint

座標と回転のコントロール用にボーンを１つ作成し、選択中のCurveにContraintをつけてボーンをターゲットに設定する。追加されるConstraintは全て名前がAHT_で始まります。

## Remove AHT Constraints

選択中のCurveから、AHT\_で始まるConstraintを全て削除する。
「Create Bone and Constraint」で作成したConstraintの削除用。

## Select Shape Key

選択中のCurveで、AHTという名前のShapeKeyがなければ作成し、選択状態にしてValueの値を1.0にする。

## Reset AHT Shape Value

選択中のCurveで、AHTという名前のShapeKeyを選択状態にしてValueの値を0.0にする。

