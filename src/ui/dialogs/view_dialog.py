"""
表示/編集ダイアログ
訂正依頼の詳細表示と編集（ロック済みは編集不可）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QCheckBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate

from ...config import ATTENDANCE_TYPES, GRADE_TYPES, SEMESTER_TYPES, PERIOD_TYPES
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ViewDialog(QDialog):
    """表示/編集ダイアログ"""
    
    def __init__(self, correction, students, courses, parent=None):
        super().__init__(parent)
        self.correction = correction
        self.students = students
        self.courses = courses
        self.is_locked = correction.get('is_locked', False)
        
        self.setWindowTitle("訂正依頼詳細")
        self.resize(600, 700)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # ロック状態表示
        if self.is_locked:
            lock_label = QLabel(f"🔒 ロック済み（{self.correction.get('locked_by', '')}）")
            lock_label.setStyleSheet("background-color: #FFE4E1; padding: 10px; font-weight: bold;")
            layout.addWidget(lock_label)
        
        # フォーム
        form_layout = QFormLayout()
        
        # 依頼種別
        self.request_type_label = QLabel()
        form_layout.addRow("依頼種別:", self.request_type_label)
        
        # 生徒選択
        self.student_combo = QComboBox()
        self.student_combo.setEnabled(not self.is_locked)
        for student in self.students:
            display_text = f"{student['class_number']} {student['name']}"
            self.student_combo.addItem(display_text, student['student_id'])
        form_layout.addRow("生徒:", self.student_combo)
        
        # 講座選択
        self.course_combo = QComboBox()
        self.course_combo.setEnabled(not self.is_locked)
        for course in self.courses:
            self.course_combo.addItem(course['course_name'], course['course_id'])
        form_layout.addRow("講座:", self.course_combo)
        
        # 対象日付（出欠訂正の場合）
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(not self.is_locked)
        self.date_widget = QGroupBox("対象日付")
        date_layout = QVBoxLayout()
        date_layout.addWidget(self.date_edit)
        self.date_widget.setLayout(date_layout)
        form_layout.addRow(self.date_widget)
        
        # 学期（出欠訂正の場合）
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(SEMESTER_TYPES)
        self.semester_combo.setEnabled(not self.is_locked)
        self.semester_widget = QGroupBox("学期")
        semester_layout = QVBoxLayout()
        semester_layout.addWidget(self.semester_combo)
        self.semester_widget.setLayout(semester_layout)
        form_layout.addRow(self.semester_widget)
        
        # 校時（出欠訂正の場合）
        self.period_checkboxes = []
        period_widget = QGroupBox("校時")
        period_layout = QHBoxLayout()
        for period in PERIOD_TYPES:
            cb = QCheckBox(period)
            cb.setEnabled(not self.is_locked)
            self.period_checkboxes.append(cb)
            period_layout.addWidget(cb)
        period_widget.setLayout(period_layout)
        self.period_widget = period_widget
        form_layout.addRow(self.period_widget)
        
        # 訂正前
        self.before_combo = QComboBox()
        self.before_combo.setEnabled(not self.is_locked)
        form_layout.addRow("訂正前:", self.before_combo)
        
        # 訂正後
        self.after_combo = QComboBox()
        self.after_combo.setEnabled(not self.is_locked)
        form_layout.addRow("訂正後:", self.after_combo)
        
        # 理由
        self.reason_edit = QTextEdit()
        self.reason_edit.setReadOnly(self.is_locked)
        form_layout.addRow("理由:", self.reason_edit)
        
        # 依頼者
        self.requester_label = QLabel()
        form_layout.addRow("依頼者:", self.requester_label)
        
        # 依頼日時
        self.request_datetime_label = QLabel()
        form_layout.addRow("依頼日時:", self.request_datetime_label)
        
        layout.addLayout(form_layout)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        if not self.is_locked:
            save_btn = QPushButton("編集")
            save_btn.clicked.connect(self.accept)
            button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """データをロード"""
        # 依頼種別
        request_type = self.correction['request_type']
        self.request_type_label.setText(request_type)
        
        # 生徒
        student_id = self.correction['student_id']
        for i in range(self.student_combo.count()):
            if self.student_combo.itemData(i) == student_id:
                self.student_combo.setCurrentIndex(i)
                break
        
        # 講座
        course_id = self.correction['course_id']
        for i in range(self.course_combo.count()):
            if self.course_combo.itemData(i) == course_id:
                self.course_combo.setCurrentIndex(i)
                break
        
        # 出欠訂正の場合
        if request_type == "出欠訂正":
            self.before_combo.addItems(ATTENDANCE_TYPES)
            self.after_combo.addItems(ATTENDANCE_TYPES)
            
            # 対象日付
            if self.correction.get('target_date'):
                date = QDate.fromString(self.correction['target_date'], "yyyy-MM-dd")
                self.date_edit.setDate(date)
            
            # 学期
            if self.correction.get('semester'):
                index = self.semester_combo.findText(self.correction['semester'])
                if index >= 0:
                    self.semester_combo.setCurrentIndex(index)
            
            # 校時
            if self.correction.get('periods'):
                selected_periods = self.correction['periods'].split(',')
                for cb in self.period_checkboxes:
                    period_num = cb.text().replace('限', '')
                    if period_num in selected_periods:
                        cb.setChecked(True)
            
            self.semester_widget.show()
            self.period_widget.show()
            self.date_widget.show()
        else:
            # 評価評定変更の場合
            self.before_combo.addItems(GRADE_TYPES)
            self.after_combo.addItems(GRADE_TYPES)
            
            self.semester_widget.hide()
            self.period_widget.hide()
            self.date_widget.hide()
        
        # 訂正前
        if self.correction.get('before_value'):
            index = self.before_combo.findText(self.correction['before_value'])
            if index >= 0:
                self.before_combo.setCurrentIndex(index)
        
        # 訂正後
        if self.correction.get('after_value'):
            index = self.after_combo.findText(self.correction['after_value'])
            if index >= 0:
                self.after_combo.setCurrentIndex(index)
        
        # 理由
        self.reason_edit.setPlainText(self.correction.get('reason', ''))
        
        # 依頼者
        self.requester_label.setText(self.correction.get('requester_name', ''))
        
        # 依頼日時
        self.request_datetime_label.setText(self.correction.get('request_datetime', '')[:19])
    
    def get_data(self):
        """入力データを取得"""
        data = {}
        
        request_type = self.request_type_label.text()
        data['request_type'] = request_type
        
        if request_type == "出欠訂正":
            data['target_date'] = self.date_edit.date().toString("yyyy-MM-dd")
            data['semester'] = self.semester_combo.currentText()
            
            selected_periods = []
            for cb in self.period_checkboxes:
                if cb.isChecked():
                    selected_periods.append(cb.text().replace('限', ''))
            data['periods'] = ','.join(selected_periods)
        
        data['before_value'] = self.before_combo.currentText()
        data['after_value'] = self.after_combo.currentText()
        data['reason'] = self.reason_edit.toPlainText()
        
        return data
