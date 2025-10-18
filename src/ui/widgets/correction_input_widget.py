"""
訂正入力ウィジェット
複数の入力フォームを管理
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QMessageBox, QLabel, QRadioButton,
    QButtonGroup, QComboBox, QTextEdit, QDateEdit,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from typing import List, Dict, Any

from ...config import (
    REQUEST_TYPES, ATTENDANCE_TYPES, SEMESTER_TYPES, PERIOD_TYPES,
    COLOR_ATTENDANCE, COLOR_GRADE
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CorrectionFormWidget(QWidget):
    """個別の訂正入力フォーム"""
    
    remove_requested = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.students = []
        self.courses = []
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 削除ボタン
        remove_btn = QPushButton("❌ このフォームを削除")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)
        
        # 訂正種別
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("訂正種別:"))
        
        self.type_group = QButtonGroup()
        self.attendance_radio = QRadioButton("出欠訂正")
        self.grade_radio = QRadioButton("評価評定変更")
        self.attendance_radio.setChecked(True)
        
        self.type_group.addButton(self.attendance_radio)
        self.type_group.addButton(self.grade_radio)
        
        type_layout.addWidget(self.attendance_radio)
        type_layout.addWidget(self.grade_radio)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # 種別変更時のイベント
        self.attendance_radio.toggled.connect(self.on_type_changed)
        
        # 依頼者
        requester_layout = QHBoxLayout()
        requester_layout.addWidget(QLabel("依頼者:"))
        self.requester_input = QComboBox()
        self.requester_input.setEditable(True)
        requester_layout.addWidget(self.requester_input)
        layout.addLayout(requester_layout)
        
        # 生徒選択
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel("生徒:"))
        self.student_combo = QComboBox()
        self.student_combo.setEditable(True)
        self.student_combo.setInsertPolicy(QComboBox.NoInsert)
        student_layout.addWidget(self.student_combo)
        layout.addLayout(student_layout)
        
        # 講座選択
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("講座:"))
        self.course_combo = QComboBox()
        self.course_combo.setEditable(True)
        self.course_combo.setInsertPolicy(QComboBox.NoInsert)
        course_layout.addWidget(self.course_combo)
        layout.addLayout(course_layout)
        
        # 出欠訂正用フィールド
        self.attendance_group = QGroupBox("出欠訂正")
        attendance_layout = QVBoxLayout()
        
        # 対象日付
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("対象日付:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        attendance_layout.addLayout(date_layout)
        
        # 学期選択（出欠訂正用）
        semester_layout = QHBoxLayout()
        semester_layout.addWidget(QLabel("学期:"))
        self.attendance_semester_combo = QComboBox()
        self.attendance_semester_combo.addItems(SEMESTER_TYPES)
        semester_layout.addWidget(self.attendance_semester_combo)
        attendance_layout.addLayout(semester_layout)
        
        # 校時選択
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("校時:"))
        self.period_checks = []
        for period in PERIOD_TYPES[:6]:
            check = QCheckBox(period)
            self.period_checks.append(check)
            period_layout.addWidget(check)
        attendance_layout.addLayout(period_layout)
        
        period_layout2 = QHBoxLayout()
        period_layout2.addWidget(QLabel(""))
        for period in PERIOD_TYPES[6:]:
            check = QCheckBox(period)
            self.period_checks.append(check)
            period_layout2.addWidget(check)
        attendance_layout.addLayout(period_layout2)
        
        # 訂正前/後
        before_layout = QHBoxLayout()
        before_layout.addWidget(QLabel("訂正前:"))
        self.attendance_before_combo = QComboBox()
        self.attendance_before_combo.addItems(ATTENDANCE_TYPES)
        before_layout.addWidget(self.attendance_before_combo)
        attendance_layout.addLayout(before_layout)
        
        after_layout = QHBoxLayout()
        after_layout.addWidget(QLabel("訂正後:"))
        self.attendance_after_combo = QComboBox()
        self.attendance_after_combo.addItems(ATTENDANCE_TYPES)
        after_layout.addWidget(self.attendance_after_combo)
        attendance_layout.addLayout(after_layout)
        
        self.attendance_group.setLayout(attendance_layout)
        self.attendance_group.setStyleSheet(f"QGroupBox {{ background-color: {COLOR_ATTENDANCE}; }}")
        layout.addWidget(self.attendance_group)
        
        # 評価評定変更用フィールド
        self.grade_group = QGroupBox("評価評定変更")
        grade_layout = QVBoxLayout()
        
        # 学期
        grade_semester_layout = QHBoxLayout()
        grade_semester_layout.addWidget(QLabel("学期:"))
        self.grade_semester_combo = QComboBox()
        self.grade_semester_combo.addItems(SEMESTER_TYPES)
        grade_semester_layout.addWidget(self.grade_semester_combo)
        grade_layout.addLayout(grade_semester_layout)
        
        # 訂正前/後
        grade_before_layout = QHBoxLayout()
        grade_before_layout.addWidget(QLabel("訂正前:"))
        self.grade_before_input = QComboBox()
        self.grade_before_input.setEditable(True)
        grade_before_layout.addWidget(self.grade_before_input)
        grade_layout.addLayout(grade_before_layout)
        
        grade_after_layout = QHBoxLayout()
        grade_after_layout.addWidget(QLabel("訂正後:"))
        self.grade_after_input = QComboBox()
        self.grade_after_input.setEditable(True)
        grade_after_layout.addWidget(self.grade_after_input)
        grade_layout.addLayout(grade_after_layout)
        
        self.grade_group.setLayout(grade_layout)
        self.grade_group.setStyleSheet(f"QGroupBox {{ background-color: {COLOR_GRADE}; }}")
        self.grade_group.setVisible(False)
        layout.addWidget(self.grade_group)
        
        # 理由
        layout.addWidget(QLabel("理由:"))
        self.reason_edit = QTextEdit()
        self.reason_edit.setMaximumHeight(80)
        layout.addWidget(self.reason_edit)
        
        self.setLayout(layout)
    
    def on_type_changed(self):
        """訂正種別が変更された時"""
        is_attendance = self.attendance_radio.isChecked()
        self.attendance_group.setVisible(is_attendance)
        self.grade_group.setVisible(not is_attendance)
    
    def set_students(self, students: List[Dict[str, Any]]):
        """生徒リストを設定"""
        self.students = students
        self.student_combo.clear()
        self.student_combo.addItem("", None)
        
        for student in students:
            display_text = f"{student['class_number']} {student['name']}"
            self.student_combo.addItem(display_text, student['student_id'])
    
    def set_courses(self, courses: List[Dict[str, Any]]):
        """講座リストを設定"""
        self.courses = courses
        self.course_combo.clear()
        self.course_combo.addItem("", None)
        
        for course in courses:
            self.course_combo.addItem(course['course_name'], course['course_id'])
    
    def get_data(self) -> Dict[str, Any]:
        """入力データを取得"""
        is_attendance = self.attendance_radio.isChecked()
        
        # 選択された校時を取得
        selected_periods = [
            check.text().replace("限", "") 
            for check in self.period_checks 
            if check.isChecked()
        ]
        
        data = {
            'request_type': REQUEST_TYPES['ATTENDANCE'] if is_attendance else REQUEST_TYPES['GRADE'],
            'requester': self.requester_input.currentText().strip(),
            'student_id': self.student_combo.currentData(),
            'course_id': self.course_combo.currentData(),
            'reason': self.reason_edit.toPlainText().strip()
        }
        
        if is_attendance:
            data.update({
                'target_date': self.date_edit.date().toString('yyyy-MM-dd'),
                'semester': self.attendance_semester_combo.currentText(),
                'periods': ','.join(selected_periods) if selected_periods else None,
                'before_value': self.attendance_before_combo.currentText(),
                'after_value': self.attendance_after_combo.currentText()
            })
        else:
            data.update({
                'semester': self.grade_semester_combo.currentText(),
                'before_value': self.grade_before_input.currentText().strip(),
                'after_value': self.grade_after_input.currentText().strip()
            })
        
        return data
    
    def set_data(self, data: Dict[str, Any]):
        """データをフォームに設定（複製用）"""
        # 訂正種別
        if data.get('request_type') == REQUEST_TYPES['ATTENDANCE']:
            self.attendance_radio.setChecked(True)
        else:
            self.grade_radio.setChecked(True)
        
        # 依頼者
        if data.get('requester'):
            self.requester_input.setCurrentText(data['requester'])
        
        # 生徒
        if data.get('student_id'):
            index = self.student_combo.findData(data['student_id'])
            if index >= 0:
                self.student_combo.setCurrentIndex(index)
        
        # 講座
        if data.get('course_id'):
            index = self.course_combo.findData(data['course_id'])
            if index >= 0:
                self.course_combo.setCurrentIndex(index)
        
        # 理由
        if data.get('reason'):
            self.reason_edit.setPlainText(data['reason'])
        
        # 出欠訂正の場合
        if data.get('request_type') == REQUEST_TYPES['ATTENDANCE']:
            if data.get('target_date'):
                self.date_edit.setDate(QDate.fromString(data['target_date'], 'yyyy-MM-dd'))
            
            if data.get('semester'):
                index = self.attendance_semester_combo.findText(data['semester'])
                if index >= 0:
                    self.attendance_semester_combo.setCurrentIndex(index)
            
            if data.get('periods'):
                periods = data['periods'].split(',')
                for check in self.period_checks:
                    period_num = check.text().replace("限", "")
                    check.setChecked(period_num in periods)
            
            if data.get('before_value'):
                index = self.attendance_before_combo.findText(data['before_value'])
                if index >= 0:
                    self.attendance_before_combo.setCurrentIndex(index)
            
            if data.get('after_value'):
                index = self.attendance_after_combo.findText(data['after_value'])
                if index >= 0:
                    self.attendance_after_combo.setCurrentIndex(index)
        
        # 評価評定変更の場合
        else:
            if data.get('semester'):
                index = self.grade_semester_combo.findText(data['semester'])
                if index >= 0:
                    self.grade_semester_combo.setCurrentIndex(index)
            
            if data.get('before_value'):
                self.grade_before_input.setCurrentText(data['before_value'])
            
            if data.get('after_value'):
                self.grade_after_input.setCurrentText(data['after_value'])
    
    def clear(self):
        """フォームをクリア"""
        self.attendance_radio.setChecked(True)
        self.requester_input.setCurrentIndex(0)
        self.student_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())
        self.attendance_semester_combo.setCurrentIndex(0)
        
        for check in self.period_checks:
            check.setChecked(False)
        
        self.attendance_before_combo.setCurrentIndex(0)
        self.attendance_after_combo.setCurrentIndex(0)
        self.grade_semester_combo.setCurrentIndex(0)
        self.grade_before_input.setCurrentText("")
        self.grade_after_input.setCurrentText("")
        self.reason_edit.clear()
    
    def validate(self) -> tuple[bool, str]:
        """入力内容を検証"""
        if not self.requester_input.currentText().strip():
            return False, "依頼者を入力してください"
        
        if not self.student_combo.currentData():
            return False, "生徒を選択してください"
        
        if not self.course_combo.currentData():
            return False, "講座を選択してください"
        
        if not self.reason_edit.toPlainText().strip():
            return False, "理由を入力してください"
        
        is_attendance = self.attendance_radio.isChecked()
        
        if is_attendance:
            selected_periods = [check for check in self.period_checks if check.isChecked()]
            if len(selected_periods) > 2:
                return False, "校時は最大2つまで選択できます"
        else:
            if not self.grade_after_input.currentText().strip():
                return False, "訂正後の値を入力してください"
        
        return True, ""


class CorrectionInputWidget(QWidget):
    """訂正入力ウィジェット（複数フォーム管理）"""
    
    submit_requested = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.forms: List[CorrectionFormWidget] = []
        self.setup_ui()
        self.add_form()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 入力フォームを複製")
        add_btn.clicked.connect(self.duplicate_form)
        button_layout.addWidget(add_btn)
        
        submit_btn = QPushButton("✅ 確認して登録")
        submit_btn.clicked.connect(self.on_submit)
        button_layout.addWidget(submit_btn)
        
        clear_btn = QPushButton("🗑️ 全てクリア")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.forms_container = QWidget()
        self.forms_layout = QVBoxLayout()
        self.forms_layout.addStretch()
        self.forms_container.setLayout(self.forms_layout)
        
        scroll.setWidget(self.forms_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def add_form(self):
        """新しいフォームを追加"""
        form = CorrectionFormWidget()
        form.remove_requested.connect(self.remove_form)
        
        # 既存のデータを引き継ぐ
        if self.forms:
            form.set_students(self.forms[0].students)
            form.set_courses(self.forms[0].courses)
        
        self.forms.append(form)
        self.forms_layout.insertWidget(len(self.forms) - 1, form)
    
    def duplicate_form(self):
        """最後のフォームを複製"""
        if not self.forms:
            self.add_form()
            return
        
        # 最後のフォームのデータを取得
        last_form = self.forms[-1]
        data = last_form.get_data()
        
        # 新しいフォームを追加
        form = CorrectionFormWidget()
        form.remove_requested.connect(self.remove_form)
        form.set_students(last_form.students)
        form.set_courses(last_form.courses)
        
        # データを設定
        form.set_data(data)
        
        self.forms.append(form)
        self.forms_layout.insertWidget(len(self.forms) - 1, form)
        
        logger.info("フォームを複製しました")
    
    def remove_form(self, form: CorrectionFormWidget):
        """フォームを削除"""
        if len(self.forms) <= 1:
            QMessageBox.warning(self, "警告", "最後のフォームは削除できません")
            return
        
        self.forms.remove(form)
        self.forms_layout.removeWidget(form)
        form.deleteLater()
    
    def set_students(self, students: List[Dict[str, Any]]):
        """全フォームに生徒リストを設定"""
        for form in self.forms:
            form.set_students(students)
    
    def set_courses(self, courses: List[Dict[str, Any]]):
        """全フォームに講座リストを設定"""
        for form in self.forms:
            form.set_courses(courses)
    
    def on_submit(self):
        """登録ボタンがクリックされた時"""
        corrections = []
        
        for i, form in enumerate(self.forms):
            valid, error = form.validate()
            if not valid:
                QMessageBox.warning(self, "入力エラー", 
                    f"フォーム{i+1}: {error}")
                return
            
            corrections.append(form.get_data())
        
        self.submit_requested.emit(corrections)
    
    def clear_all(self):
        """全フォームをクリア"""
        reply = QMessageBox.question(
            self, "確認", 
            "全ての入力内容をクリアしますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 最初のフォーム以外を削除
            while len(self.forms) > 1:
                form = self.forms.pop()
                self.forms_layout.removeWidget(form)
                form.deleteLater()
            
            # 最初のフォームをクリア
            if self.forms:
                self.forms[0].clear()
