from models import database as db
from views.building_view import AddBuildingDialogUI
from views.base_dialog import ConfirmDialog

class BuildingController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)

    def load_data(self):
        self.view.update_grid(db.get_buildings())

    def show_add_dialog(self):
        AddBuildingDialogUI(self.view, self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_building(data["name"], data["floors"], data["desc"])
        dlg._close()
        self.load_data()

    def show_edit_dialog(self, building):
        AddBuildingDialogUI(self.view, self._handle_edit, prefill=building)

    def _handle_edit(self, data, dlg):
        bid = dlg.prefill['id']
        db.update_building(bid, data["name"], data["floors"], data["desc"])
        dlg._close()
        self.load_data()

    def confirm_delete(self, parent, building):
        ConfirmDialog(parent,
            message=f"Xóa tòa nhà '{building['name']}'?\nTất cả phòng trống trong tòa cũng bị xóa.",
            on_confirm=lambda: self._do_delete(building['id']),
            confirm_text="🗑  Xóa tòa nhà", danger=True)

    def _do_delete(self, bid):
        db.delete_building(bid)
        self.load_data()
