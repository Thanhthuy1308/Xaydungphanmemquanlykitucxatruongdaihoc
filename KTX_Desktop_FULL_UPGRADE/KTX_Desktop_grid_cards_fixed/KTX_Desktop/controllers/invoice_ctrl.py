from models import database as db
from views.base_dialog import ConfirmDialog
from views.invoice_view import AddInvoiceDialogUI, fmt_money


class InvoiceController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._raw = []
        self._last_month = None
        self._last_status = "Tất cả"
        self._last_search = ""

    def load_data(self, month, status="Tất cả", search=""):
        self._last_month = month
        self._last_status = status
        self._last_search = search
        st_map = {"Tất cả": None, "Chưa thanh toán": "unpaid", "Đã thanh toán": "paid"}
        self._raw = db.get_invoices(month=month, status=st_map.get(status), search=search)
        summary = db.get_invoice_summary(month)
        rows = []
        for inv in self._raw:
            room = f"{inv.get('building_name','?')} P.{inv.get('room_number','?')}" if inv.get("room_number") else "—"
            action = "Thu tiền" if inv["payment_status"] == "unpaid" else "Hủy thu"
            rows.append([
                inv["sid"], inv["fullname"], room, inv.get("created_date", "")[:10],
                fmt_money(inv.get("room_fee")),
                fmt_money((inv.get("electric_fee") or 0) + (inv.get("water_fee") or 0) + (inv.get("violation_fee") or 0)),
                fmt_money(inv.get("total_amount")),
                "✓ Đã thu" if inv["payment_status"] == "paid" else "⏳ Chưa thu",
                action,
            ])
        self.view.update_ui(self._raw, rows, summary)

    def _reload(self):
        self.load_data(self._last_month, self._last_status, self._last_search)

    def show_add_dialog(self):
        AddInvoiceDialogUI(self.view, db.get_students_for_invoice(), self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_invoice(
            data["student_id"], data["room_fee"], data["electric_fee"],
            data["water_fee"], data["violation_fee"], data["payment_status"],
            data["created_date"], data["note"]
        )
        dlg._close()
        self.view.set_month(data["created_date"][:7])
        self.view.set_status("Tất cả")
        self.load_data(data["created_date"][:7], "Tất cả", self._last_search)

    def toggle_paid(self, idx):
        if idx >= len(self._raw):
            return
        inv = self._raw[idx]
        if inv["payment_status"] == "unpaid":
            ConfirmDialog(
                self.view,
                message=f"Thu hóa đơn cho {inv['fullname']}?\nTổng tiền: {fmt_money(inv['total_amount'])}",
                on_confirm=lambda: (db.mark_invoice_paid(inv["id"]), self._reload()),
                confirm_text="💰  Thu tiền",
                title="Xác nhận thu hóa đơn"
            )
        else:
            ConfirmDialog(
                self.view,
                message=f"Hủy xác nhận đã thu hóa đơn của {inv['fullname']}?",
                on_confirm=lambda: (db.mark_invoice_unpaid(inv["id"]), self._reload()),
                confirm_text="↩  Hủy thu",
                danger=True
            )
