from datetime import date

from models import database as db
from views.invoice_view import fmt_money


class RevenueReportController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)

    def load_data(self, month=None):
        month = month or date.today().strftime("%Y-%m")
        report = db.get_revenue_report(month)
        rows = []
        for inv in report["invoices"]:
            rows.append([
                inv["sid"],
                inv["fullname"],
                inv.get("building_name") or "—",
                fmt_money(inv.get("total_amount")),
                "✓ Đã thu" if inv["payment_status"] == "paid" else "⏳ Chưa thu",
            ])
        self.view.update_ui(month, report["summary"], report["by_building"], rows)
