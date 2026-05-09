from models import database as db
from views.room_view import AddRoomDialogUI, RoomDetailDialog
from views.base_dialog import ConfirmDialog

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except: return "0đ"

class RoomController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._rooms = []
        self._last_status = "Tất cả"
        self._last_bid    = None
        self._last_floor = None

    def load_data(self, status="Tất cả", building_id=None, floor=None):
        self._last_status = status
        self._last_bid    = building_id
        self._last_floor = floor
        st_map = {"Tất cả":None,"Còn trống":"available","Đang ở":"occupied","Bảo trì":"maintenance"}
        self._rooms = db.get_rooms(building_id=building_id, status=st_map.get(status))
        if floor:
            self._rooms = [r for r in self._rooms if int(r.get('floor',0)) == floor]
        buildings   = db.get_buildings()
        self.view.set_building_options(buildings)
        st_lbl = {"available":"✓ Trống","occupied":"● Đang ở","maintenance":"⚠ Bảo trì"}
        rows = [[r['room_number'], r['building_name'], r['floor'],
                 "VIP" if r['type']=='vip' else "Thường",
                 f"{r['capacity']} người", f"{r['current_occupants']}/{r['capacity']}",
                 fmt_money(r['price']), st_lbl.get(r['status'],r['status']),
                 "👁 Xem / ✏ Sửa"] for r in self._rooms]
        self.view.update_table(self._rooms, rows)

    def _reload(self):
        self.load_data(self._last_status, self._last_bid, self._last_floor)

    def show_detail(self, idx):
        if idx >= len(self._rooms): return
        RoomDetailDialog(self.view, self._rooms[idx], self)

    def show_add_dialog(self):
        AddRoomDialogUI(self.view, db.get_buildings(), self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_room(data["bid"], data["rnum"], data["floor"],
                    data["cap"], data["rtype"], data["price"])
        dlg._close()
        self._reload()

    def show_edit_dialog(self, room):
        AddRoomDialogUI(self.view, db.get_buildings(), self._handle_edit, prefill=room)

    def _handle_edit(self, data, dlg):
        db.update_room(dlg.prefill['id'], data["rnum"], data["floor"],
                       data["cap"], data["rtype"], data["price"], data["status"])
        dlg._close()
        self._reload()

    def confirm_delete_room(self, parent, room):
        ConfirmDialog(parent,
            message=f"Xóa phòng {room['room_number']} — {room['building_name']}?",
            on_confirm=lambda: self._do_delete(room['id']),
            confirm_text="🗑  Xóa phòng", danger=True)

    def _do_delete(self, rid):
        db.delete_room(rid)
        self._reload()
