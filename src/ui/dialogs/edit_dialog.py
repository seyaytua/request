"""
訂正依頼編集ダイアログ
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit,
    QDateEdit, QRadioButton, QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt, QDate
from typing import Dict, Any, List

from ...config import ATTENDANCE_TYPES, GRADE_TYPES, SEMESTER_TYPES, PERIOD_TYPES


class EditDialog(QDialog):
    """訂正依頼編集ダイアログ"""
    
    def __init__(self, correction: Dict[str, Any], students: List[Dict], 
                 courses: List[Dict], parent=None):
        super().__init__(parent)
        self.correction = correction
        self.students = students
        self.courses = courses
        self.setWindowTitle("訂正依頼編集")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # 依頼種別（変更不可）
        type_label = QLabel(f"依頼種別: {self.correction['request_type']}")
        type_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(type_label)
        
        # フォーム
        form = QFormLayout()
        
        # 生徒選択
        self.student_combo = QComboBox()
        for student in self.students:
            display_text = f"{student['class_number']} {student['name']}"
            self.student_combo.addItem(display_text, student['student_id'])
        form.addRow("生徒:", self.student_combo)
        
        # 講座選択
        self.course_combo = QComboBox()
        for course in self.courses:
            self.course_combo.addItem(course['course_name'], course['course_id'])
        form.addRow("講座:", self.course_combo)
        
        # 出欠訂正の場合
        if self.correction['request_type'] == '出欠訂正':
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDisplayFormat("yyyy-MM-dd")
            form.addRow("対象日付:", self.date_edit)
            
            self.semester_combo = QComboBox()
            self.semester_combo.addItems(SEMESTER_TYPES)
            form.addRow("学期:", self.semester_combo)
            
            period_group = QGroupBox("校時選択（最大2つ）")
            period_layout = QVBoxLayout()
            self.period_checkboxes = {}
            for period in PERIOD_TYPES:
                checkbox = QRadioButton(period)
                self.period_checkboxes[period] = checkbox
                period_layout.addWidget(checkbox)
            period_group.setLayout(period_layout)
            form.addRow(period_group)
            
            self.before_combo = QComboBox()
            self.before_combo.addItems(ATTENDANCE_TYPES)
            form.addRow("訂正前:", self.before_combo)
            
            self.after_combo = QComboBox()
            self.after_combo.addItems(ATTENDANCE_TYPES)
            form.addRow("訂正後:", self.after_combo)
        
        # 評価評定変更の場合
        else:
            self.semester_combo = QComboBox()
            self.semester_combo.addItems(SEMESTER_TYPES)
            form.addRow("学期:", self.semester_combo)
            
            self.before_combo = QComboBox()
            self.before_combo.addItems(GRADE_TYPES)
            form.addRow("訂正前:", self.before_combo)
            
            self.after_combo = QComboBox()
            self.after_combo.addItems(GRADE_TYPES)
            form.addRow("訂正後:", self.after_combo)
        
        # 理由
        self.reason_edit = QTextEdit()
        self.reason_edit.setMaximumHeight(100)
        form.addRow("理由:", self.reason_edit)
        
        layout.addLayout(form)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """既存データをロード"""
        # 生徒選択
        for i in range(self.student_combo.count()):
            if self.student_combo.itemData(i) == self.correction['student_id']:
                self.student_combo.setCurrentIndex(i)
                break
        
        # 講座選択
        for i in range(self.course_combo.count()):
            if self.course_combo.itemData(i) == self.correction['course_id']:
                self.course_combo.setCurrentIndex(i)
                break
        
        # 出欠訂正の場合
        if self.correction['request_type'] == '出欠訂正':
            if self.correction.get('target_date'):
                date = QDate.fromString(self.correction['target_date'], "yyyy-MM-dd")
                self.date_edit.setDate(date)
            
            if self.correction.get('semester'):
                index = self.semester_combo.findText(self.correction['semester'])
                if index >= 0:
                    self.semester_combo.setCurrentIndex(index)
            
            if self.correction.get('periods'):
                periods = self.correction['periods'].split(',')
                for period in periods:
                    period_text = f"{period}限"
                    if period_text in self.period_checkboxes:
                        self.period_checkboxes[period_text].setChecked(True)
            
            if self.correction.get('before_value'):
                index = self.before_combo.findText(self.correction['before_value'])
                if index >= 0:
                    self.before_combo.setCurrentIndex(index)
            
            if self.correction.get('after_value'):
                index = self.after_combo.findText(self.correction['after_value'])
                if index >= 0:
                    self.after_combo.setCurrentIndex(index)
        
        # 評価評定変更の場合
        else:
            if self.correction.get('semester'):
                index = self.semester_combo.findText(self.correction['semester'])
                if index >= 0:
                    self.semester_combo.setCurrentIndex(index)
            
            if self.correction.get('before_value'):
                index = self.before_combo.findText(self.correction['before_value'])
                if index >= 0:
                    self.before_combo.setCurrentIndex(index)
            
            if self.correction.get('after_value'):
                index = self.after_combo.findText(self.correction['after_value'])
                if index >= 0:
                    self.after_combo.setCurrentIndex(index)
        
        # 理由
        if self.correction.get('reason'):
            self.reason_edit.setPlainText(self.correction['reason'])
    
    def get_data(self) -> Dict[str, Any]:
        """編集後のデータを取得"""
        data = {
            'student_id': self.student_combo.currentData(),
            'course_id': self.course_combo.currentData(),
            'before_value': self.before_combo.currentText(),
            'after_value': self.after_combo.currentText(),
            'reason': self.reason_edit.toPlainText()
        }
        
        if self.correction['request_type'] == '出欠訂正':
            data['target_date'] = self.date_edit.date().toString("yyyy-MM-dd")
            data['semester'] = self.semester_combo.currentText()
            
            selected_periods = []
            for period, checkbox in self.period_checkboxes.items():
                if checkbox.isChecked():
                    selected_periods.append(period.replace('限', ''))
            data['periods'] = ','.join(selected_periods) if selected_periods else None
        else:
            data['semester'] = self.semester_combo.currentText()
        
        return data
