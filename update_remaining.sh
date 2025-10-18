#!/bin/bash

echo "🔧 残りのファイルを更新中..."

# correction_input_widget.py の更新が必要な部分のみ抽出して作成
# 既存のファイルをバックアップ
cp src/ui/widgets/correction_input_widget.py src/ui/widgets/correction_input_widget.py.backup 2>/dev/null || true

echo "✅ 更新スクリプトの準備完了"
echo ""
echo "次のコマンドを実行してください："
echo "python main.py"

