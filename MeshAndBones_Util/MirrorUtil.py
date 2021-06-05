# Mirror Modifire Utility

# =================================================================================================
# Mirrorモディファイアを検出する
def find_mirror_modifires(obj):
    find_list = []

    # ミラーモディファイアを探して保存
    for modifier in obj.modifiers:
        if modifier.show_viewport and modifier.type == 'MIRROR':
            find_list.append(modifier)

    return find_list

# Mirrorモディファイアを検出してDisableに
def disable_mirror_modifires(obj):
    find_list = find_mirror_modifires(obj)

    # 見つけたMirrorを非表示にして無効化
    for modifire in find_list:
        modifire.show_viewport = False

    return find_list

# Mirrorモディファイアのリストを表示に戻す(disable_mirror_modifiresの戻り値を使う)
def recovery_mirror_modifires(recovery_list):
    for modifier in recovery_list:
        modifier.show_viewport = True
