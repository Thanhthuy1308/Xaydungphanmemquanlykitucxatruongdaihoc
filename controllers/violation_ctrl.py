from models import database as db
from views.violation_view import AddViolationDialogUI
from views.base_dialog import ConfirmDialog

class ViolationController:
    def __init__(self, view, current_user_id):
        self.view = view
        self.view.set_controller(self)
        self.uid  = current_user_id
        self._raw = []
        self._last_status = "Chưa xử lý"

    def load_data(self, status="Chưa xử lý"):
        self._last_status = status
        st_map = {"Chưa xử lý":"open","Đã xử lý":"resolved","Tất cả":None}
        self._raw = db.get_violations(status=st_map.get(status))
        sev = {"minor":"Nhẹ","medium":"Trung bình","severe":"Nghiêm trọng"}
        rows = [[v['student_name'],v['type'],sev.get(v['severity'],'?'),
                 f"{float(v['fine']):,.0f}đ",v.get('reporter_name','—'),
                 v['reported_at'][:10],
                  "● Chưa xử lý" if v['status']=='open' else "✓ Đã xử lý",
                  "Xử lý" if v['status']=='open' else ""] for v in self._raw]
        self.view.update_table(rows)

    def resolve(self, idx):
        if idx >= len(self._raw): return
        v = self._raw[idx]
        if v['status']=='open':
            ConfirmDialog(self.view,
                message=f"Xác nhận đã xử lý vi phạm?\nSinh viên: {v['student_name']}\nLoại: {v['type']}",
                on_confirm=lambda:(db.resolve_violation(v['id']), self.load_data(self._last_status)),
                confirm_text="✓  Đã xử lý")

    def show_add_dialog(self):
        AddViolationDialogUI(self.view, db.get_students(), self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_violation(data["student_id"],data["vtype"],data["desc"],
                         data["severity"],data["fine"],self.uid)
        dlg._close()
        self.load_data(self._last_status)
