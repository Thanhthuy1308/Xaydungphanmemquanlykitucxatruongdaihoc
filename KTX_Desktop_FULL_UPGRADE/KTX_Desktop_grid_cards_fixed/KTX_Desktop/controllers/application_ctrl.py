from models import database as db
from views.application_view import ApproveDialog, AddApplicationDialogUI

class ApplicationController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._raw = []
        self._last_status = "Đang chờ"

    def load_data(self, status="Đang chờ"):
        self._last_status = status
        st_map = {"Đang chờ":"pending","Đã duyệt":"approved","Từ chối":"rejected","Tất cả":None}
        self._raw = db.get_applications(status=st_map.get(status))
        st_lbl = {"pending":"⏳ Đang chờ","approved":"✓ Đã duyệt","rejected":"✕ Từ chối"}
        rows = [[a['fullname'], a.get('student_id','—'), a.get('gender','—'),
                 a.get('faculty','—'), a.get('preferred_room_type','standard'),
                 a['created_at'][:10], st_lbl.get(a['status'],a['status']),
                  "Xét duyệt" if a['status']=='pending' else "Xem"] for a in self._raw]
        self.view.update_table(rows)

    def show_detail(self, idx):
        if idx >= len(self._raw): return
        ApproveDialog(self.view, self._raw[idx], on_done=lambda: self.load_data(self._last_status))

    def show_add_dialog(self):
        AddApplicationDialogUI(self.view, self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_application(data["fullname"], data["student_id"], data["gender"],
                           data["phone"], data["email"], data["faculty"],
                           data["reason"], data["preferred"])
        dlg._close()
        self.load_data(self._last_status)
