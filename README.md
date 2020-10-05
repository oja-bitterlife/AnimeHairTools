# AnimeHairTools

## 概要

アニメ風の髪の毛をCurve(Path)で作るのに手数を減らしたい、そんなツールです。

Curveのコントロールポイント上にボーンを配置しフックを設定するので、ボーンを使ってCurveを簡単に動かせます。

### 作例
|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/maribe.jpg" width="256px" height="256px">|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/emeruda.jpg" width="256px" height="256px">|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/sorano.jpg" width="256px" height="256px">|

まだインストーラとかないので、普通にスクリプトタブからファイルを取り込んで実行しないと動きません。
プラグインが起動すると、オブジェクトモード時に３Dビュー上にAnimeHairToolsというメニューが追加されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/3d-view.jpg">

## 使い方

とりあえず使うだけなら

1. Setup Armature and RootBone ボタンを押す
1. ボーンをつけたいCurve(Pathのみ。bezie非対応)を選択して、Create ChildBone And Hook ボタンを押す

これだけで、ArmatureがRootシーンの直下に作成され、ボーンがCurveのコントロールポイントに沿って生成されます。

Curve以外のオブジェクトが選択されていても無視するので、まとめてオブジェクトを選択しても大丈夫です。

※bezieは多分10行も追加すれば対応できるんだけど、自分が髪の毛には使わないので非対応にしてます。

## Armature and Bone Setting

ツール用のArmatureを作成します。髪の毛のBoneは顔のボーンに追従することが多いはずなので、Constraint Target には通常、顔のBoneを設定しておきます。そうすると、顔の位置にRootBoneが生成されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/ATH_Armature_setup.jpg" width="50%" height="50%">


あとからConstraint先を変えてこのボタンを押すと、今までのBoneの座標がおかしくなりますが、Create ChildBone And Settings ボタンを押し直せばBoneが生成され直すので、慌てず再度Boneを作り直してください。

## Create ChildBone and Hook

選択中のCurveごとにコントロールポイント間の連結Boneが作成され、自動でHook Modifierが生成されCurveのPointにHookされます。

実行前にRemoveが実行されるので、やり直すときは単純にこのボタンを押し直すだけですみます。

## Remove AnimeHairTools Bone and Hook

選択中のCurveから Create ChildBone and Hook で自動生成されたものを削除します。

* ArmaturよりBoneの削除
* CurveよりHook Modifierの削除
