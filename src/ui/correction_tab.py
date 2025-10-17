"""
訂正入力タブ
左65%にリスト、右35%に入力フォーム
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt

from .widgets.correction_list_widget import CorrectionListWidget
from .widgets.correction_input_widget import CorrectionInputWidget
from .dialogs.confirmation_dialog import ConfirmationDialog
from ..controllers.correction_controller import CorrectionController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CorrectionTab(QWidget):
    """訂正入力タブ"""
    
    def __init__(self, correction_controller: CorrectionController, parent=None):
        super().__init__(parent)
        self.controller = correction_controller
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QHBoxLayout()
        
        # スプリッター（左65%、右35%）
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側: 訂正依頼リスト
        self.list_widget = CorrectionListWidget()
        self.list_widget.refresh_requested.connect(self.refresh_list)
        
        # 右側: 訂正入力フォーム
        self.input_widget = CorrectionInputWidget()
        self.input_widget.submit_requested.connect(self.on_submit_corrections)
        
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.input_widget)
        
        # 幅の比率を設定（65:35）
        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_data(self):
        """データをロード"""
        try:
            # 生徒と講座をロード
            students = self.controller.get_students(year=2024)
            courses = self.controller.get_courses(year=2024)
            
            self.input_widget.set_students(students)
            self.input_widget.set_courses(courses)
            
            # 訂正依頼リストをロード
            self.refresh_list()
            
            logger.info("データをロードしました")
            
        except Exception as e:
            logger.error(f"データのロードに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"データのロードに失敗しました:\n{e}")
    
    def refresh_list(self):
        """訂正依頼リストを更新"""
        try:
            corrections = self.controller.get_corrections(limit=1000)
            self.list_widget.load_corrections(corrections)
            logger.info(f"{len(corrections)}件の訂正依頼をロードしました")
            
        except Exception as e:
            logger.error(f"訂正依頼リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼リストの更新に失敗しました:\n{e}")
    
    def on_submit_corrections(self, corrections: list):
        """訂正依頼を送信（確認ダイアログを順次表示）"""
        success_count = 0
        
        for i, correction_data in enumerate(corrections):
            # 確認ダイアログ表示
            dialog = ConfirmationDialog(correction_data, self)
            result = dialog.exec()
            
            if result == ConfirmationDialog.Accepted:
                try:
                    # データベースに保存
                    correction_id = self.controller.create_correction(correction_data)
                    success_count += 1
                    logger.info(f"訂正依頼を登録しました: ID={correction_id}")
                    
                except Exception as e:
                    logger.error(f"訂正依頼の登録に失敗: {e}")
                    QMessageBox.critical(self, "エラー", 
                        f"訂正依頼の登録に失敗しました:\n{e}")
                    break
            else:
                # キャンセルされた場合
                remaining = len(corrections) - i
                if remaining > 1:
                    reply = QMessageBox.question(
                        self, "確認", 
                        f"残り{remaining}件の訂正をキャンセルしますか？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        break
                else:
                    break
        
        # 完了メッセージ
        if success_count > 0:
            QMessageBox.information(
                self, "完了", 
                f"{success_count}件の訂正依頼を登録しました"
            )
            
            # リストを更新
            self.refresh_list()
            
            # フォームをクリア
            self.input_widget.clear_all()
