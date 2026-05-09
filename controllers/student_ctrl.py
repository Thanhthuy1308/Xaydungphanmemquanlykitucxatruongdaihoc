from models import database as db
from views.student_view import AddStudentDialogUI, StudentDetailDialog
from views.base_dialog import ConfirmDialog

class StudentController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._raw = []
        self._last_search = ""
        self._last_status = "Đang ở"

    def load_data(self, search="", status="Đang ở"):
        self._last_search = search
        self._last_status = status
        db_status = "active" if status == "Đang ở" else "checked_out"
        self._raw = db.get_students(search=search, status=db_status)
        rows = []
        for s in self._raw:
            room = f"{s['building_name']} P.{s['room_number']}" if s.get('room_number') else "—"
            rows.append([s['student_id'], s['fullname'], s.get('faculty','—'),
                         room, s.get('phone','—'), s.get('checkin_date','—'), "Chi tiết"])
        self.view.update_table(rows)

    def _reload(self):
        self.load_data(self._last_search, self._last_status)

    def show_add_dialog(self):
        AddStudentDialogUI(self.view, db.get_available_rooms(), self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_student(data["sid"], data["name"], data["gender"], data["dob"],
                       data["phone"], data["email"], data["faculty"], data["cls"],
                       data["room_id"], data["checkin"])
        dlg._close()
        self._reload()

    def show_detail(self, idx):
        if idx >= len(self._raw): return
        StudentDetailDialog(self.view, self._raw[idx]['id'], on_done=self._reload)

    def confirm_delete(self, parent, student):
        ConfirmDialog(parent,
            message=f"Xóa sinh viên: {student['fullname']}?\nMSSV: {student['student_id']}",
            on_confirm=lambda: self._do_delete(student['id']),
            confirm_text="🗑  Xóa sinh viên", danger=True)

    def _do_delete(self, sid):
        db.delete_student(sid)
        self._reload()
