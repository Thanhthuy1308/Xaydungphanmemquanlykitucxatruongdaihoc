from models import database as db
from views.staff_view import AddStaffDialogUI
from views.base_dialog import ConfirmDialog

class StaffController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._raw = []

    def load_data(self):
        self._raw = db.get_staff()
        rows = [[s['username'], s['fullname'] or '—', s.get('position','—'),
                 s.get('shift','—'), s.get('building_name','—'),
                 s.get('phone','—'), "Xóa"] for s in self._raw]
        self.view.update_table(rows)

    def show_add_dialog(self):
        AddStaffDialogUI(self.view, db.get_buildings(), self._handle_add)

    def _handle_add(self, data, dlg):
        ok = db.add_staff(data["username"], data["password"], data["fullname"],
                          data["phone"], data["position"], data["shift"], data["building_id"])
        if ok:
            dlg._close(); self.load_data()
        else:
            import tkinter.messagebox as mb
            mb.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")

    def confirm_delete(self, idx):
        if idx >= len(self._raw): return
        s = self._raw[idx]
        ConfirmDialog(self.view,
            message=f"Xóa nhân viên: {s['fullname'] or s['username']}?",
            on_confirm=lambda: (db.delete_staff(s['id']), self.load_data()),
            confirm_text="🗑  Xóa", danger=True)
