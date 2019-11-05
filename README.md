# AnimeHairTools

アニメ風の髪の毛をCurveで作るのに手数を減らしたい、そんなツール。

## Bevel & Taper Setting

選択中のCurveにBevelとTaperを一括で設定する。メイン機能。

## Material Setting

選択中のCurveのMaterialを一括で変更する。

マテリアルがすでにSlotにあればそれを使う。SlotになければSlotを追加してそこにマテリアルを設定して使う。

## Create Bone and Constraint

座標と回転のコントロール用にボーンを１つ作成し、選択中のCurveにContraintをつけてボーンをターゲットに設定する。

## Remove AHT Constraints

選択中のCurveから、AHT\_で始まるConstraintを全て削除する

## Select Shape Key

選択中のCurveで、AHTという名前のShapeKeyがなければ作成し、選択状態にしてValueの値を1.0にする。

# Reset AHT Shape Value

選択中のCurveで、AHTという名前のShapeKeyを選択状態にしてValueの値を0.0にする。

