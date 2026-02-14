import customtkinter as ctk
import requests
import threading
from tkinter import messagebox

# --- CẤU HÌNH ---
# Link Server của bạn
API_URL = "https://api-dan-cu.onrender.com/api"

# Thiết lập giao diện
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class AppPhieuKhaoSat(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG QUẢN LÝ DÂN CƯ (PC)")
        self.geometry("1100x700")

        # Layout chính: Chia làm 2 cột
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === CỘT TRÁI: FORM NHẬP LIỆU ===
        self.frame_left = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_left.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self.frame_left, text="PHIẾU RÀ SOÁT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#ef4444")
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.lbl_status = ctk.CTkLabel(self.frame_left, text="Trạng thái: Đang chờ...", text_color="gray")
        self.lbl_status.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.scroll_form = ctk.CTkScrollableFrame(self.frame_left, label_text="Nhập thông tin")
        self.scroll_form.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # --- CÁC TRƯỜNG NHẬP LIỆU ---
        self.entries = {} 
        self.add_input("Họ và tên người khai (*)", "ho_ten")
        self.add_input("Ngày sinh (dd/mm/yyyy)", "ngay_sinh")
        self.add_dropdown("Giới tính", "gio_tinh", ["Nam", "Nữ"])
        self.add_input("Địa chỉ thường trú", "thuong_tru")
        self.add_input("Nơi ở hiện tại", "noi_o_hien_tai")
        self.add_input("Số CMND/CCCD", "so_cmnd")
        self.add_input("Ngày cấp", "ngay_cap")
        self.add_input("Nơi cấp", "noi_cap", default="Cục CS QLHC về TTXH")
        self.add_input("Quê quán", "que_quan")
        self.add_input("Dân tộc", "dan_toc", default="Kinh")
        self.add_input("Số điện thoại (*)", "sdt")
        self.add_dropdown("Công việc", "nghe_nghiep", ["Đang có việc làm", "Thất nghiệp", "Hưu trí", "Học sinh"])

        self.btn_save = ctk.CTkButton(self.frame_left, text="LƯU DỮ LIỆU", height=50, fg_color="#b91c1c", hover_color="#991b1b", font=ctk.CTkFont(size=16, weight="bold"), command=self.gui_phieu)
        self.btn_save.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # === CỘT PHẢI: DANH SÁCH ===
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_list = ctk.CTkLabel(self.frame_right, text="DANH SÁCH TỪ SERVER", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_list.pack(pady=10)

        self.btn_refresh = ctk.CTkButton(self.frame_right, text="🔄 Làm mới danh sách", command=self.tai_danh_sach_thread, fg_color="gray")
        self.btn_refresh.pack(pady=5)

        self.scroll_list = ctk.CTkScrollableFrame(self.frame_right)
        self.scroll_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Tự động tải danh sách khi mở App (Chạy ngầm)
        self.tai_danh_sach_thread()

    # --- HÀM HỖ TRỢ GIAO DIỆN ---
    def add_input(self, label, key, default=""):
        ctk.CTkLabel(self.scroll_form, text=label, anchor="w").pack(fill="x", pady=(5, 0))
        entry = ctk.CTkEntry(self.scroll_form)
        entry.pack(fill="x", pady=(2, 5))
        if default: entry.insert(0, default)
        self.entries[key] = entry

    def add_dropdown(self, label, key, values):
        ctk.CTkLabel(self.scroll_form, text=label, anchor="w").pack(fill="x", pady=(5, 0))
        option = ctk.CTkOptionMenu(self.scroll_form, values=values)
        option.pack(fill="x", pady=(2, 5))
        self.entries[key] = option

    # --- XỬ LÝ SERVER (CHẠY NGẦM) ---
    def tai_danh_sach_thread(self):
        self.lbl_status.configure(text="Đang tải dữ liệu...", text_color="orange")
        # Chạy trong luồng riêng để không treo máy
        threading.Thread(target=self.tai_danh_sach_backend).start()

    def tai_danh_sach_backend(self):
        try:
            print("--> Đang gọi Server...")
            res = requests.get(f"{API_URL}/danh-sach", timeout=10)
            if res.status_code == 200:
                data = res.json()
                # Cập nhật giao diện phải dùng luồng chính
                self.after(0, lambda: self.hien_thi_danh_sach(data))
            else:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Không tải được danh sách"))
        except Exception as e:
            print(f"Lỗi: {e}")
            self.after(0, lambda: self.bao_loi_ket_noi(str(e)))

    def hien_thi_danh_sach(self, data):
        self.lbl_status.configure(text=f"Đã tải xong: {len(data)} phiếu", text_color="green")
        # Xóa cũ
        for widget in self.scroll_list.winfo_children():
            widget.destroy()
        
        # Vẽ mới
        for item in data:
            card = ctk.CTkFrame(self.scroll_list, fg_color="#334155")
            card.pack(fill="x", pady=5, padx=5)
            
            # Tên
            ctk.CTkLabel(card, text=str(item.get('ho_ten', 'Không tên')).upper(), font=ctk.CTkFont(size=16, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=10, pady=(10, 0))
            
            # Thông tin
            info = f"CMND: {item.get('so_cmnd', '')}  |  SĐT: {item.get('sdt', '')}  |  🏠 {item.get('thuong_tru', '')}"
            ctk.CTkLabel(card, text=info, text_color="#cbd5e1").pack(anchor="w", padx=10, pady=(0, 10))

    def bao_loi_ket_noi(self, err):
        self.lbl_status.configure(text="Mất kết nối Server!", text_color="red")
        messagebox.showerror("Lỗi Mạng", f"Không kết nối được Server.\nChi tiết: {err}")

    def gui_phieu(self):
        # Thu thập dữ liệu
        data = {k: v.get() for k, v in self.entries.items()}
        if not data['ho_ten'] or not data['sdt']:
            messagebox.showwarning("Thiếu thông tin", "Nhập tên và SĐT!")
            return

        def run_post():
            try:
                requests.post(f"{API_URL}/gui-phieu", json=data)
                self.after(0, lambda: messagebox.showinfo("Thành công", "Đã lưu!"))
                self.tai_danh_sach_thread() # Tải lại danh sách
            except:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Gửi thất bại"))

        threading.Thread(target=run_post).start()

if __name__ == "__main__":
    app = AppPhieuKhaoSat()
    app.mainloop()