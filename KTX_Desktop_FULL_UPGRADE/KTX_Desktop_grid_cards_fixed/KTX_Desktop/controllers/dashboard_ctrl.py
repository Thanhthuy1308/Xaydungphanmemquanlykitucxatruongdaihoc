from models import database as db
from datetime import datetime

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)

    def load_data(self):
        stats = db.get_dashboard_stats()
        occupancy = db.get_occupancy_by_building()
        viols = db.get_violations(status='open')[:5]
        
        # Format lại dữ liệu vi phạm cho bảng
        viol_rows = []
        if viols:
            sev_map = {"minor":"Nhẹ","medium":"Trung bình","severe":"Nghiêm trọng"}
            viol_rows = [[v['student_name'], v['type'], sev_map.get(v['severity'],'—')] for v in viols]

        self.view.update_dashboard(stats, occupancy, viol_rows)