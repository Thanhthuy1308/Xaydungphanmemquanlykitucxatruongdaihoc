from datetime import datetime

class MainController:
    def __init__(self, main_window, current_user):
        self.main_window   = main_window
        self.current_user  = current_user
        self._pages        = {}
        self._controllers  = {}

    def switch_page(self, page_id):
        for p in self._pages.values():
            p.grid_forget()
        if page_id not in self._pages:
            self._create_page(page_id)
        if page_id in self._pages:
            self._pages[page_id].grid(row=0, column=0, sticky="nsew")
            if page_id in self._controllers:
                ctrl = self._controllers[page_id]
                if   page_id == "violations":   ctrl.load_data("Chưa xử lý")
                elif page_id == "payments":     ctrl.load_data(datetime.now().strftime("%Y-%m"), "Tất cả")
                elif page_id == "invoices":     ctrl.load_data(datetime.now().strftime("%Y-%m"), "Tất cả")
                elif page_id == "revenue":      ctrl.load_data(datetime.now().strftime("%Y-%m"))
                elif page_id == "rooms":        ctrl.load_data("Tất cả")
                elif page_id == "students":     ctrl.load_data("", "Đang ở")
                elif page_id == "applications": ctrl.load_data("Đang chờ")
                else:                           ctrl.load_data()

    def _create_page(self, page_id):
        cf = self.main_window.content

        if page_id == "dashboard":
            from views.dashboard_view import DashboardPage
            from controllers.dashboard_ctrl import DashboardController
            view = DashboardPage(cf, self.current_user['fullname'])
            ctrl = DashboardController(view)

        elif page_id == "buildings":
            from views.building_view import BuildingsPage
            from controllers.building_ctrl import BuildingController
            view = BuildingsPage(cf)
            ctrl = BuildingController(view)

        elif page_id == "rooms":
            from views.room_view import RoomsPage
            from controllers.room_ctrl import RoomController
            view = RoomsPage(cf)
            ctrl = RoomController(view)

        elif page_id == "students":
            from views.student_view import StudentsPage
            from controllers.student_ctrl import StudentController
            view = StudentsPage(cf)
            ctrl = StudentController(view)

        elif page_id == "payments":
            from views.payment_view import PaymentsPage
            from controllers.payment_ctrl import PaymentController
            view = PaymentsPage(cf)
            ctrl = PaymentController(view)

        elif page_id == "invoices":
            from views.invoice_view import InvoicesPage
            from controllers.invoice_ctrl import InvoiceController
            view = InvoicesPage(cf)
            ctrl = InvoiceController(view)

        elif page_id == "violations":
            from views.violation_view import ViolationsPage
            from controllers.violation_ctrl import ViolationController
            view = ViolationsPage(cf)
            ctrl = ViolationController(view, self.current_user['id'])

        elif page_id == "applications":
            from views.application_view import ApplicationsPage
            from controllers.application_ctrl import ApplicationController
            view = ApplicationsPage(cf)
            ctrl = ApplicationController(view)

        elif page_id == "staff":
            from views.staff_view import StaffPage
            from controllers.staff_ctrl import StaffController
            view = StaffPage(cf)
            ctrl = StaffController(view)

        elif page_id == "reports":
            from views.report_view import ReportsPage
            from controllers.report_ctrl import ReportController
            view = ReportsPage(cf)
            ctrl = ReportController(view)

        elif page_id == "revenue":
            from views.revenue_report_view import RevenueReportPage
            from controllers.revenue_report_ctrl import RevenueReportController
            view = RevenueReportPage(cf)
            ctrl = RevenueReportController(view)

        else:
            return

        self._pages[page_id]       = view
        self._controllers[page_id] = ctrl
