"""
訂正入力ウィジェット
右側35%に表示される入力フォーム（スクロール可能）
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGroupBox, QFormLayout, QLabel, QComboBox, QLineEdit,
    QTextEdit, QPushButton, QDateEdit, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate
from typing import Dict, Any, List


class CorrectionInputWidget(QWidget):
    """訂正入力ウィジェット（スクロール可能）"""
    
    # シグナル定義
    submit_requested = Signal(list)  # 訂正依頼の送信リクエスト
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.forms = []  # 複数フォームを管理
        self.students = []
        self.courses = []
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # スクロール内のコンテナ
        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        
        # 複製ボタン
        duplicate_btn = QPushButton("📋 入力フォームを複製")
        duplicate_btn.clicked.connect(self.duplicate_form)
        self.container_layout.addWidget(duplicate_btn)
        
        # 最初のフォームを追加
        self.add_form()
        
        # 送信ボタン
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        
        self.submit_btn = QPushButton("✓ 確認して登録")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.submit_btn.clicked.connect(self.on_submit)
        submit_layout.addWidget(self.submit_btn)
        
        self.container_layout.addLayout(submit_layout)
        self.container_layout.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def add_form(self, copy_from: 'CorrectionForm' = None):
        """フォームを追加"""
        form = CorrectionForm(len(self.forms) + 1, copy_from)
        form.set_students(self.students)
        form.set_courses(self.courses)
        
        # 削除ボタンのシグナル接続
        form.delete_requested.connect(lambda: self.remove_form(form))
        
        # 送信ボタンの前に挿入
        self.container_layout.insertWidget(
            self.container_layout.count() - 2, form
        )
        self.forms.append(form)
        
        return form
    
    def duplicate_form(self):
        """最後のフォームを複製"""
        if self.forms:
            last_form = self.forms[-1]
            self.add_form(copy_from=last_form)
    
    def remove_form(self, form: 'CorrectionForm'):
        """フォームを削除"""
        if len(self.forms) <= 1:
            QMessageBox.warning(self, "削除不可", 
                "最低1つのフォームは必要です")
            return
        
        self.forms.remove(form)
        form.deleteLater()
        
        # フォーム番号を振り直し
        for i, f in enumerate(self.forms):
            f.set_form_number(i + 1)
    
    def on_submit(self):
        """送信ボタンが押された時"""
        corrections = []
        
        for i, form in enumerate(self.forms):
            data = form.get_data()
            
            # バリデーション
            error = form.validate()
            if error:
                QMessageBox.warning(self, "入力エラー", 
                    f"フォーム{i+1}: {error}")
                return
            
            corrections.append(data)
        
        # 確認ダイアログを表示するシグナルを発行
        self.submit_requested.emit(corrections)
    
    def set_students(self, students: List[Dict[str, Any]]):
        """生徒リストを設定"""
        self.students = students
        for form in self.forms:
            form.set_students(students)
    
    def set_courses(self, courses: List[Dict[str, Any]]):
        """講座リストを設定"""
        self.courses = courses
        for form in self.forms:
            form.set_courses(courses)
    
    def clear_all(self):
        """全フォームをクリア"""
        # 2つ目以降のフォームを削除
        while len(self.forms) > 1:
            form = self.forms.pop()
            form.deleteLater()
        
        # 最初のフォームをクリア
        if self.forms:
            self.forms[0].clear()


class CorrectionForm(QGroupBox):
    """個別の訂正入力フォーム"""
    
    delete_requested = Signal()
    
    def __init__(self, form_number: int = 1, copy_from: 'CorrectionForm' = None):
        super().__init__(f"訂正依頼 #{form_number}")
        self.form_number = form_number
        self.students = []
        self.courses = []
        self.setup_ui()
        
        # 複製元がある場合はデータをコピー
        if copy_from:
            self.copy_data_from(copy_from)
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # 依頼種別
        self.request_type = QComboBox()
        self.request_type.addItems(["出欠訂正", "評価評定変更"])
        self.request_type.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("依頼種別:", self.request_type)
        
        # 生徒選択
        self.student_combo = QComboBox()
        form_layout.addRow("生徒:", self.student_combo)
        
        # 講座選択
        self.course_combo = QComboBox()
        form_layout.addRow("講座:", self.course_combo)
        
        # 対象日付（出欠訂正の場合）
        self.target_date = QDateEdit()
        self.target_date.setDate(QDate.currentDate())
        self.target_date.setCalendarPopup(True)
        form_layout.addRow("対象日付:", self.target_date)
        
        # 学期（評価評定変更の場合）
        self.semester = QSpinBox()
        self.semester.setRange(1, 3)
        self.semester.setValue(1)
        form_layout.addRow("学期:", self.semester)
        
        # 訂正前
        self.before_value = QLineEdit()
        self.before_value.setPlaceholderText("例: 欠席 / B")
        form_layout.addRow("訂正前:", self.before_value)
        
        # 訂正後
        self.after_value = QLineEdit()
        self.after_value.setPlaceholderText("例: 出席 / A")
        form_layout.addRow("訂正後:", self.after_value)
        
        # 理由
        self.reason = QTextEdit()
        self.reason.setMaximumHeight(80)
        self.reason.setPlaceholderText("訂正理由を入力してください")
        form_layout.addRow("理由:", self.reason)
        
        layout.addLayout(form_layout)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("クリア")
        clear_btn.clicked.connect(self.clear)
        button_layout.addWidget(clear_btn)
        
        delete_btn = QPushButton("削除")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(self.delete_requested.emit)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 初期状態の表示切替
        self.on_type_changed(self.request_type.currentText())
    
    def on_type_changed(self, request_type: str):
        """依頼種別が変更された時"""
        is_attendance = (request_type == "出欠訂正")
        
        # 対象日付と学期の表示切替
        self.target_date.setVisible(is_attendance)
        self.semester.setVisible(not is_attendance)
        
        # ラベルも切り替え
        layout = self.layout().itemAt(0).layout()  # FormLayout
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            if label_item:
                label = label_item.widget()
                if isinstance(label, QLabel):
                    if "対象日付" in label.text():
                        label.setVisible(is_attendance)
                    elif "学期" in label.text():
                        label.setVisible(not is_attendance)
    
    def set_students(self, students: List[Dict[str, Any]]):
        """生徒リストを設定"""
        self.students = students
        self.student_combo.clear()
        
        for student in students:
            display_text = f"{student['name']} ({student['class_number']})"
            self.student_combo.addItem(display_text, student['student_id'])
    
    def set_courses(self, courses: List[Dict[str, Any]]):
        """講座リストを設定"""
        self.courses = courses
        self.course_combo.clear()
        
        for course in courses:
            display_text = f"{course['course_name']} ({course['teacher_name']})"
            self.course_combo.addItem(display_text, course['course_id'])
    
    def get_data(self) -> Dict[str, Any]:
        """入力データを取得"""
        student_id = self.student_combo.currentData()
        course_id = self.course_combo.currentData()
        request_type = self.request_type.currentText()
        
        # 生徒名と講座名を取得（確認ダイアログ用）
        student_name = self.student_combo.currentText()
        course_name = self.course_combo.currentText()
        
        data = {
            'request_type': request_type,
            'student_id': student_id,
            'course_id': course_id,
            'student_name': student_name,
            'course_name': course_name,
            'before_value': self.before_value.text(),
            'after_value': self.after_value.text(),
            'reason': self.reason.toPlainText()
        }
        
        if request_type == "出欠訂正":
            data['target_date'] = self.target_date.date().toString("yyyy-MM-dd")
        else:
            data['semester'] = self.semester.value()
        
        return data
    
    def validate(self) -> str:
        """入力をバリデーション（エラーメッセージを返す）"""
        if not self.student_combo.currentData():
            return "生徒を選択してください"
        
        if not self.course_combo.currentData():
            return "講座を選択してください"
        
        if not self.after_value.text():
            return "訂正後の値を入力してください"
        
        if not self.reason.toPlainText():
            return "理由を入力してください"
        
        return None
    
    def clear(self):
        """フォームをクリア"""
        self.student_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.before_value.clear()
        self.after_value.clear()
        self.reason.clear()
        self.target_date.setDate(QDate.currentDate())
        self.semester.setValue(1)
    
    def copy_data_from(self, other: 'CorrectionForm'):
        """他のフォームからデータをコピー"""
        self.request_type.setCurrentText(other.request_type.currentText())
        self.course_combo.setCurrentIndex(other.course_combo.currentIndex())
        self.after_value.setText(other.after_value.text())
        # 生徒、対象日付、理由は新規入力
    
    def set_form_number(self, number: int):
        """フォーム番号を設定"""
        self.form_number = number
        self.setTitle(f"訂正依頼 #{number}")
