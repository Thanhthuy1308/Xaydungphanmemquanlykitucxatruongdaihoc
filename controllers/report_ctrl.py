
from models import database as db
from collections import Counter

class ReportController:
    def __init__(self, view):
        self.view = view
        self.view.set_controller(self)

    def load_data(self):
        # 1. Lấy dữ liệu lấp đầy tòa nhà
        occupancy = db.get_occupancy_by_building()
        
        # 2. Lấy dữ liệu doanh thu
        revenue = db.get_revenue_chart()
        
        # 3. Lấy dữ liệu vi phạm và gom nhóm đếm số lượng
        viols = db.get_violations()
        vtypes_counter = Counter(v['type'] for v in viols)
        # Chuyển thành dạng list [(Loại vi phạm, Số lượng), ...] lấy 8 lỗi phổ biến nhất
        violation_counts = vtypes_counter.most_common(8)
        
        # 4. Truyền toàn bộ dữ liệu đã xử lý sang View để vẽ
        self.view.update_ui(occupancy, revenue, violation_counts)