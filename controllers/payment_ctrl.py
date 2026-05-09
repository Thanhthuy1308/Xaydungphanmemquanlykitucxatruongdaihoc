from models import database as db
from views.payment_view import AddPaymentDialogUI, GeneratePaymentDialogUI, fmt_money
from views.base_dialog import ConfirmDialog

class PaymentController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)
        self._raw = []
        self._last_month  = None
        self._last_status = "Tất cả"

    def load_data(self, month, status):
        self._last_month  = month
        self._last_status = status
        st_map = {"Tất cả": None, "Chưa thu": "pending", "Đã thu": "paid"}
        self._raw = db.get_payments(month=month, status=st_map.get(status))
        summ = db.get_payment_summary(month)
        rows = []
        for p in self._raw:
            room   = f"{p.get('building_name','?')} P.{p.get('room_number','?')}" if p.get('room_number') else "—"
            action = "Thu tiền" if p['status']=='pending' else "Hủy thu"
            rows.append([p['sid'], p['fullname'], room, p['month'],
                         fmt_money(p['amount']),
                         "✓ Đã thu" if p['status']=='paid' else "⏳ Chờ thu",
                         p.get('paid_date','—'), action])
        self.view.update_ui(self._raw, rows, summ)

    def _reload(self):
        self.load_data(self._last_month, self._last_status)

    def toggle_paid(self, idx):
        if idx >= len(self._raw): return
        p = self._raw[idx]
        if p['status'] == 'pending':
            ConfirmDialog(self.view,
                message=f"Thu tiền phòng tháng {p['month']}\nSinh viên: {p['fullname']}\nSố tiền: {fmt_money(p['amount'])}",
                on_confirm=lambda: (db.mark_paid(p['id']), self._reload()),
                confirm_text="💰  Thu tiền", title="Xác nhận thu tiền")
        else:
            ConfirmDialog(self.view,
                message=f"Hủy xác nhận đã thu tháng {p['month']}\nSinh viên: {p['fullname']}?",
                on_confirm=lambda: (db.unmark_paid(p['id']), self._reload()),
                confirm_text="↩  Hủy thu", danger=True)

    # kept for backward compat
    def mark_as_paid(self, idx): self.toggle_paid(idx)

    def show_add_dialog(self):
        students = db.get_students_for_payment()
        AddPaymentDialogUI(self.view, students, self._handle_add)

    def _handle_add(self, data, dlg):
        db.add_payment(data["student_id"], data["amount"], data["month"], data["note"])
        dlg._close()
        self.view.set_month(data["month"])
        self.view.set_status("Tất cả")
        self.load_data(data["month"], "Tất cả")

    def show_generate_dialog(self):
        GeneratePaymentDialogUI(self.view, self._handle_generate)

    def _handle_generate(self, data, dlg):
        month = data["month"]
        count = db.generate_payments(month)
        collected = None
        if data.get("collect_now"):
            collected = db.mark_pending_payments_paid(month)
        dlg._close()
        if collected:
            self.view.show_message(
                f"✅  Đã tạo {count} phiếu thu cho tháng {month}.\n"
                f"Đã thu {collected['count']} phiếu, tổng {fmt_money(collected['total'])}."
            )
        else:
            self.view.show_message(f"✅  Đã tạo {count} phiếu thu cho tháng {month}!")
        self.view.set_month(month)
        self.view.set_status("Tất cả")
        self.load_data(month, "Tất cả")

    def bulk_collect(self, month):
        pending = db.get_payments(month=month, status="pending")
        if not pending:
            self.view.show_message(f"Tháng {month} không có phiếu chưa thu.")
            return
        total = sum(float(p.get("amount") or 0) for p in pending)
        ConfirmDialog(self.view,
            message=(
                f"Thu hàng loạt {len(pending)} phiếu chưa thu tháng {month}?\n"
                f"Tổng tiền: {fmt_money(total)}"
            ),
            on_confirm=lambda: self._do_bulk_collect(month),
            confirm_text="✅  Thu tất cả",
            title="Thu tiền hàng loạt")

    def _do_bulk_collect(self, month):
        info = db.mark_pending_payments_paid(month)
        self.view.show_message(
            f"✅  Đã thu {info['count']} phiếu tháng {month}.\n"
            f"Tổng tiền: {fmt_money(info['total'])}."
        )
        self.view.set_month(month)
        self.view.set_status("Tất cả")
        self.load_data(month, "Tất cả")
