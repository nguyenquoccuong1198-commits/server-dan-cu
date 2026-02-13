import customtkinter as ctk
import requests
from tkinter import messagebox
from datetime import datetime

# --- CẤU HÌNH ---
# Thay link Render của bạn vào đây
API_URL = "https://api-dan-cu.onrender.com/api"

# Thiết lập giao diện
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class AppPhieuKhaoSat(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG QUẢN LÝ DÂN CƯ (PC)")
        self.geometry("1100x700")

        # Layout chính: Chia làm 2 cột (Trái: Nhập liệu - Phải: Danh sách)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === CỘT TRÁI: FORM NHẬP LIỆU ===
        self.frame_left = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_left.grid_rowconfigure(2, weight=1) # Để thanh cuộn hoạt động

        # Tiêu đề
        self.lbl_title = ctk.CTkLabel(self.frame_left, text="PHIẾU RÀ SOÁT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#ef4444")
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.lbl_subtitle = ctk.CTkLabel(self.frame_left, text="Thông tin hộ dân (Nội bộ)", font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Khu vực cuộn cho Form (Vì form dài)
        self.scroll_form = ctk.CTkScrollableFrame(self.frame_left, label_text="Nhập thông tin chi tiết")
        self.scroll_form.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # --- CÁC TRƯỜNG NHẬP LIỆU ---
        self.entries = {} # Lưu trữ các ô nhập liệu

        self.add_input("Họ và tên người khai (*)", "ho_ten")
        self.add_row_input("Ngày sinh (dd/mm/yyyy)", "ngay_sinh", "Giới tính", "gio_tinh", is_option=True, options=["Nam", "Nữ"])
        self.add_input("Địa chỉ thường trú", "thuong_tru")
        self.add_input("Nơi ở hiện tại", "noi_o_hien_tai")
        self.add_row_input("Số CMND/CCCD", "so_cmnd", "Ngày cấp", "ngay_cap")
        self.add_input("Nơi cấp", "noi_cap", default="Cục CS QLHC về TTXH")
        self.add_input("Quê quán", "que_quan")
        self.add_row_input("Dân tộc", "dan_toc", "Tôn giáo", "ton_giao", default1="Kinh", default2="Không")
        self.add_input("Số điện thoại (*)", "sdt")
        self.add_dropdown("Công việc hiện tại", "nghe_nghiep", ["Đang có việc làm", "Thất nghiệp", "Hưu trí", "Học sinh"])

        # Nút Gửi
        self.btn_save = ctk.CTkButton(self.frame_left, text="LƯU PHIẾU KHẢO SÁT", height=50, fg_color="#b91c1c", hover_color="#991b1b", font=ctk.CTkFont(size=16, weight="bold"), command=self.gui_phieu)
        self.btn_save.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # === CỘT PHẢI: DANH SÁCH ===
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_list = ctk.CTkLabel(self.frame_right, text="DANH SÁCH ĐÃ NHẬP", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_list.pack(pady=10)

        self.btn_refresh = ctk.CTkButton(self.frame_right, text="Làm mới danh sách", command=self.tai_danh_sach, fg_color="gray")
        self.btn_refresh.pack(pady=5)

        self.scroll_list = ctk.CTkScrollableFrame(self.frame_right)
        self.scroll_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Tải dữ liệu ban đầu
        self.tai_danh_sach()

    # --- HÀM HỖ TRỢ TẠO GIAO DIỆN ---
    def add_input(self, label, key, default=""):
        ctk.CTkLabel(self.scroll_form, text=label, anchor="w").pack(fill="x", pady=(10, 0))
        entry = ctk.CTkEntry(self.scroll_form, placeholder_text=label)
        entry.pack(fill="x", pady=(5, 0))
        if default: entry.insert(0, default)
        self.entries[key] = entry

    def add_dropdown(self, label, key, values):
        ctk.CTkLabel(self.scroll_form, text=label, anchor="w").pack(fill="x", pady=(10, 0))
        option = ctk.CTkOptionMenu(self.scroll_form, values=values)
        option.pack(fill="x", pady=(5, 0))
        self.entries[key] = option

    def add_row_input(self, l1, k1, l2, k2, is_option=False, options=[], default1="", default2=""):
        frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        frame.pack(fill="x", pady=(10, 0))
        
        # Cột 1
        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f1, text=l1, anchor="w").pack(fill="x")
        e1 = ctk.CTkEntry(f1)
        e1.pack(fill="x")
        if default1: e1.insert(0, default1)
        self.entries[k1] = e1

        # Cột 2
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f2, text=l2, anchor="w").pack(fill="x")
        if is_option:
            e2 = ctk.CTkOptionMenu(f2, values=options)
        else:
            e2 = ctk.CTkEntry(f2)
            if default2: e2.insert(0, default2)
        e2.pack(fill="x")
        self.entries[k2] = e2

    # --- XỬ LÝ DỮ LIỆU ---
    def gui_phieu(self):
        # Thu thập dữ liệu từ các ô
        data = {}
        for key, widget in self.entries.items():
            data[key] = widget.get()
        
        # Kiểm tra bắt buộc
        if not data['ho_ten'] or not data['sdt']:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Họ tên và SĐT!")
            return

        # Gửi lên Server
        try:
            res = requests.post(f"{API_URL}/gui-phieu", json=data)
            if res.status_code == 200:
                messagebox.showinfo("Thành công", "Đã lưu phiếu vào hệ thống!")
                self.tai_danh_sach()
                # Xóa ô nhập tên để nhập người tiếp theo
                self.entries['ho_ten'].delete(0, "end")
            else:
                messagebox.showerror("Lỗi", "Server không phản hồi")
        except Exception as e:
            messagebox.showerror("Lỗi Mạng", f"Không kết nối được Server: {e}")

    def tai_danh_sach(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        try:
            res = requests.get(f"{API_URL}/danh-sach")
            if res.status_code == 200:
                ds = res.json()
                for item in ds:
                    self.tao_the_nguoi_dan(item)
        except:
            pass

    def tao_the_nguoi_dan(self, item):
        card = ctk.CTkFrame(self.scroll_list, fg_color="#334155")
        card.pack(fill="x", pady=5, padx=5)

        # Dòng 1: Tên to
        ctk.CTkLabel(card, text=item['ho_ten'], font=ctk.CTkFont(size=16, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=10, pady=(10, 0))
        
        # Dòng 2: Thông tin phụ
        info = f"🏠 {item['thuong_tru']}  |  📞 {item['sdt']}  |  💼 {item['nghe_nghiep']}"
        ctk.CTkLabel(card, text=info, text_color="#cbd5e1").pack(anchor="w", padx=10, pady=(0, 10))

if __name__ == "__main__":
    app = AppPhieuKhaoSat()
    app.mainloop()