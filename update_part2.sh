#!/bin/bash

echo "🔧 Part 2: システム部管理機能の更新を開始します..."
echo ""

# システム部管理タブの更新
echo "📝 システム部管理タブを更新中..."
cat > src/ui/admin_tab.py << 'EOF'
"""
システム部管理タブ
ロック管理、インポート/エクスポート、ログビューア
"""
import csv
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QGroupBox, QFileDialog
)
from PySide6.QtCore import Qt

from ..controllers.correction_controller import CorrectionController
from ..controllers.log_controller import LogController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AdminTab(QWidget):
    """システム部管理タブ"""
    
    def __init__(
        self, 
        correction_controller: CorrectionController,
        log_controller: LogController,
        parent=None
    ):
        super().__init__(parent)
        self.correction_controller = correction_controller
        self.log_controller = log_controller
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # データ管理エリア
        data_group = QGroupBox("データ管理")
        data_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 CSVエクスポート")
        export_btn.clicked.connect(self.export_to_csv)
        data_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 CSVインポート")
        import_btn.clicked.connect(self.import_from_csv)
        data_layout.addWidget(import_btn)
        
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # 訂正依頼管理エリア
        correction_group = QGroupBox("訂正依頼管理")
        correction_layout = QVBoxLayout()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_correction_list)
        button_layout.addWidget(refresh_btn)
        
        lock_btn = QPushButton("🔒 選択した依頼をロック")
        lock_btn.clicked.connect(self.lock_selected)
        button_layout.addWidget(lock_btn)
        
        unlock_btn = QPushButton("🔓 選択した依頼のロックを解除")
        unlock_btn.clicked.connect(self.unlock_selected)
        button_layout.addWidget(unlock_btn)
        
        button_layout.addStretch()
        correction_layout.addLayout(button_layout)
        
        # 訂正依頼リスト
        self.correction_table = QTableWidget()
        self.correction_table.setColumnCount(8)
        self.correction_table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "講座名", "理由", "依頼者", "ロック者", "ロック日時"
        ])
        self.correction_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.correction_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.correction_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        correction_layout.addWidget(self.correction_table)
        correction_group.setLayout(correction_layout)
        
        layout.addWidget(correction_group)
        
        # 操作ログエリア
        log_group = QGroupBox("操作ログ")
        log_layout = QVBoxLayout()
        
        log_button_layout = QHBoxLayout()
        refresh_log_btn = QPushButton("🔄 ログ更新")
        refresh_log_btn.clicked.connect(self.refresh_logs)
        log_button_layout.addWidget(refresh_log_btn)
        log_button_layout.addStretch()
        
        log_layout.addLayout(log_button_layout)
        
        # ログテーブル
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "日時", "ユーザー", "PC名", "操作種別", "対象テーブル", "詳細"
        ])
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        log_header = self.log_table.horizontalHeader()
        log_header.setStretchLastSection(True)
        
        log_layout.addWidget(self.log_table)
        log_group.setLayout(log_layout)
        
        layout.addWidget(log_group)
        
        self.setLayout(layout)
    
    def load_data(self):
        """データをロード"""
        self.refresh_correction_list()
        self.refresh_logs()
    
    def refresh_correction_list(self):
        """訂正依頼リストを更新"""
        try:
            corrections = self.correction_controller.get_corrections(limit=1000)
            
            self.correction_table.setRowCount(0)
            
            for correction in corrections:
                row = self.correction_table.rowCount()
                self.correction_table.insertRow(row)
                
                self.correction_table.setItem(row, 0, 
                    QTableWidgetItem(str(correction['correction_id'])))
                self.correction_table.setItem(row, 1, 
                    QTableWidgetItem(correction['request_type']))
                self.correction_table.setItem(row, 2, 
                    QTableWidgetItem(correction.get('student_name', '')))
                self.correction_table.setItem(row, 3, 
                    QTableWidgetItem(correction.get('course_name', '')))
                self.correction_table.setItem(row, 4, 
                    QTableWidgetItem(correction.get('reason', '')[:30] + '...'))
                self.correction_table.setItem(row, 5, 
                    QTableWidgetItem(correction.get('requester_name', '')))
                self.correction_table.setItem(row, 6, 
                    QTableWidgetItem(correction.get('locked_by', '')))
                self.correction_table.setItem(row, 7, 
                    QTableWidgetItem(correction.get('locked_datetime', '')[:16] 
                                   if correction.get('locked_datetime') else ''))
            
            logger.info(f"{len(corrections)}件の訂正依頼をロードしました")
            
        except Exception as e:
            logger.error(f"訂正依頼リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼リストの更新に失敗しました:\n{e}")
    
    def lock_selected(self):
        """選択された訂正依頼をロック"""
        selected_items = self.correction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ロックする項目を選択してください")
            return
        
        row = selected_items[0].row()
        correction_id = int(self.correction_table.item(row, 0).text())
        
        reply = QMessageBox.question(
            self, "確認", 
            f"訂正依頼 ID:{correction_id} をロックしますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.correction_controller.lock_correction(correction_id)
                
                if success:
                    QMessageBox.information(self, "完了", "訂正依頼をロックしました")
                    self.refresh_correction_list()
                    self.refresh_logs()
                else:
                    QMessageBox.warning(self, "失敗", "ロックに失敗しました")
                    
            except Exception as e:
                logger.error(f"ロックに失敗: {e}")
                QMessageBox.critical(self, "エラー", 
                    f"ロックに失敗しました:\n{e}")
    
    def unlock_selected(self):
        """選択された訂正依頼のロックを解除"""
        selected_items = self.correction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ロック解除する項目を選択してください")
            return
        
        row = selected_items[0].row()
        correction_id = int(self.correction_table.item(row, 0).text())
        
        reply = QMessageBox.question(
            self, "確認", 
            f"訂正依頼 ID:{correction_id} のロックを解除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.correction_controller.unlock_correction(correction_id)
                
                if success:
                    QMessageBox.information(self, "完了", "ロックを解除しました")
                    self.refresh_correction_list()
                    self.refresh_logs()
                else:
                    QMessageBox.warning(self, "失敗", "ロックの解除に失敗しました")
                    
            except Exception as e:
                logger.error(f"ロック解除に失敗: {e}")
                QMessageBox.critical(self, "エラー", 
                    f"ロック解除に失敗しました:\n{e}")
    
    def export_to_csv(self):
        """CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            corrections = self.correction_controller.get_corrections(limit=10000)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # ヘッダー
                writer.writerow([
                    'ID', '種別', '生徒ID', '生徒名', '組番号', 
                    '講座ID', '講座名', '対象日付', '学期', '校時',
                    '訂正前', '訂正後', '理由', '依頼者', '依頼者PC',
                    '状態', 'ロック', 'ロック者', 'ロック日時', '依頼日時'
                ])
                
                # データ
                for c in corrections:
                    writer.writerow([
                        c['correction_id'],
                        c['request_type'],
                        c['student_id'],
                        c.get('student_name', ''),
                        c.get('class_number', ''),
                        c['course_id'],
                        c.get('course_name', ''),
                        c.get('target_date', ''),
                        c.get('semester', ''),
                        c.get('periods', ''),
                        c.get('before_value', ''),
                        c.get('after_value', ''),
                        c.get('reason', ''),
                        c.get('requester_name', ''),
                        c.get('requester_pc', ''),
                        c['status'],
                        '○' if c['is_locked'] else '',
                        c.get('locked_by', ''),
                        c.get('locked_datetime', ''),
                        c.get('request_datetime', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(corrections)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"CSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"CSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"CSVエクスポートに失敗しました:\n{e}")
    
    def import_from_csv(self):
        """CSVインポート（差替え）"""
        reply = QMessageBox.warning(
            self, "警告", 
            "CSVインポートは既存のデータを全て削除して置き換えます。\n"
            "この操作は取り消せません。続行しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSVインポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if len(rows) == 0:
                QMessageBox.warning(self, "警告", 
                    "CSVファイルにデータがありません（タイトル行のみ）")
                return
            
            # 既存データを全削除
            self.correction_controller.db.execute_update(
                "DELETE FROM correction_requests"
            )
            
            # インポート
            success_count = 0
            for row in rows:
                try:
                    correction_data = {
                        'request_type': row['種別'],
                        'student_id': int(row['生徒ID']),
                        'course_id': row['講座ID'],
                        'target_date': row['対象日付'] or None,
                        'semester': row['学期'] or None,
                        'periods': row['校時'] or None,
                        'before_value': row['訂正前'] or None,
                        'after_value': row['訂正後'],
                        'reason': row['理由'],
                        'requester': row['依頼者']
                    }
                    
                    self.correction_controller.create_correction(correction_data)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"行のインポートに失敗: {e}")
                    continue
            
            QMessageBox.information(self, "完了", 
                f"{success_count}件のデータをインポートしました")
            logger.info(f"CSVインポート完了: {success_count}件")
            
            self.refresh_correction_list()
            
        except Exception as e:
            logger.error(f"CSVインポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"CSVインポートに失敗しました:\n{e}")
    
    def refresh_logs(self):
        """操作ログを更新"""
        try:
            logs = self.log_controller.get_logs(limit=100)
            
            self.log_table.setRowCount(0)
            
            for log in logs:
                row = self.log_table.rowCount()
                self.log_table.insertRow(row)
                
                self.log_table.setItem(row, 0, 
                    QTableWidgetItem(log['timestamp'][:19]))
                self.log_table.setItem(row, 1, 
                    QTableWidgetItem(log['username']))
                self.log_table.setItem(row, 2, 
                    QTableWidgetItem(log['pc_name']))
                self.log_table.setItem(row, 3, 
                    QTableWidgetItem(log['operation_type']))
                self.log_table.setItem(row, 4, 
                    QTableWidgetItem(log['target_table']))
                self.log_table.setItem(row, 5, 
                    QTableWidgetItem(log.get('operation_detail', '')))
            
            logger.info(f"{len(logs)}件のログをロードしました")
            
        except Exception as e:
            logger.error(f"ログの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"ログの更新に失敗しました:\n{e}")
EOF

echo "✅ システム部管理タブを更新しました"

# 設計書の更新
echo "📝 設計書を更新中..."
cat > docs/01_主要機能一覧.md << 'EOF'
# 訂正依頼システム - 主要機能一覧 (v1.2.0)

## 1. 訂正入力機能
- 出欠訂正に学期フィールド追加
- 入力フォーム複製時に内容をそのまま複製
- ロックされていない訂正依頼の編集・削除

## 2. システム部管理機能
- 訂正依頼のロック機能
- CSVエクスポート/インポート機能
- 操作ログ閲覧

## 更新履歴
| 日付 | バージョン | 更新内容 |
|------|-----------|---------|
| 2025-10-18 | 1.2.0 | 学期追加、複製改善、CSV機能 |
| 2025-10-17 | 1.1.0 | 校時追加、色分け |
| 2025-10-17 | 1.0.0 | 初版作成 |
EOF

echo "✅ 設計書を更新しました"
echo ""
echo "🎉 Part 2 完了！"
echo ""
echo "次のコマンドでアプリケーションを起動:"
echo "  python main.py"
