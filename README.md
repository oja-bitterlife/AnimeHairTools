# AnimeHairTools

## 概要

アニメ風の髪の毛を Curve(Path) で作るのに手数を減らしたい、そんなツールです。

最初は Curve で完結させていたのですが、最近アニメーションをやるようになって Curve だと頭が上を向いていないと回転してしまう問題が発生しました。

|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/curve-top.png" width="256px" height="256px">|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/curve-side.png" width="256px" height="256px">

そのため Version 0.1.0 から Curve を Mesh 化して Bone を作って Weight を自動設定するツールに変更しています。

### 作例
|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/maribe.jpg" width="256px" height="256px">|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/emeruda.jpg" width="256px" height="256px">|<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/sorano.jpg" width="256px" height="256px">|

まだインストーラとかないのでスクリプトタブからファイルを取り込んで実行しないと動きません。

プラグインが起動すると、オブジェクトモード時に３Dビュー上に AnimeHairTools というメニューが追加されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/3d-view.jpg">

## 使い方

とりあえず使うだけなら

1. Setup Armature and RootBone ボタンを押して、髪の毛用 Bone を追加していく Armature を作成しておく
1. ボーンをつけたい Curve(Path のみ。bezie はまだ非対応)を選択して、Create Mesh and Bones ボタンを押す

これだけで、Armature が Root シーンの直下に作成され、Bone が Curve のコントロールポイントに沿って生成され、weight を設定済みの Curve を Mesh 化したもの(元の Curve はそのまま残ります)が生成されます。

Curve 以外のオブジェクトが選択されていても無視するので、まとめてオブジェクトを選択しても大丈夫です。

※bezie は自分が髪の毛には使わないので今の所非対応にしてます。

### Armature and Bone Setting

ツール用の Armature を作成します。髪の毛の Bone は顔のボーンに追従することが多いはずなので、Constraint Target には通常、顔の Bone を設定しておきます。そうすると、顔の位置に RootBone が生成されます。

<img src="https://github.com/oja-bitterlife/AnimeHairTools/blob/master/sample/ATH_Armature_setup.jpg" width="50%" height="50%">

既存の Armature を使う場合は Armature と Bone の項目を設定するだけで Setup Armature and RootBone ボタン を押す必要はありません。同じものがすでに存在する場合は無視され、変更点があればそこだけ反映されます。

Constraint 先を変更した場合今までのBoneの座標がおかしくなりますので、その時は再度 Create Mesh and Bones ボタンで Bone を作り直してください。メッシュごと作り直されますが大抵は問題ないと思います。

### Create Mesh and Bones

選択中のCurveごとにコントロールポイント間の連結Boneが作成され、距離を元に自動でウェイトをつけたMeshが生成され、Armature モディファイアと頂点グループが追加されます。

生成される Bone には BendyBones で設定された値がそのままプロパティに設定されます。BendyBones が不要な場合は 1 に設定してください。

CurveにMirrorモディファイアがある場合はX軸ミラーがあるものとし、生成されるMeshにMirrorモディファイアが追加され Bone も名前に.L/.R付与された Mirror 化されたものが生成されます。

実行前に Remove が実行されるので、やり直すときは単純にこのボタンを押し直すだけですみます。

### Remove Mesh and Bones

選択中の Curve を元に Create Mesh and Bones で自動生成されたものを削除します。

実際には自動生成されたかどうかは関係なく、名前の先頭に Curve 名 + @bone と、Curve 名 + @mesh がつくものを全部バッサリ削除します。

通常名前がかぶることはないと思いますが、名前がかぶる場合は勝手にオブジェクトが消されるので、このツールの使用を中止してください。

Create Mesh and Bones ボタンでも同じ Remove プログラムが動くので、名前がかぶる場合はやはり意図しないオブジェクトが削除される可能性があります。

## 手動で変更を消したい

生成された全 Mesh のオブジェクトを削除してください。その後 AnimeHairTools で生成した Armature を削除すればすべてなかったことになります。
