import customtkinter as ctk
import requests
import threading
import json
from tkinter import messagebox, filedialog
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import re

# --- CẤU HÌNH ---
API_URL = "https://api-dan-cu.onrender.com/api"
THEME_COLOR = "#B91C1C" # Đỏ VNeID

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class AppQuanLyDanCu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HỆ THỐNG QUẢN LÝ DÂN CƯ (PC)")
        self.geometry("1280x800")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=THEME_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="QUẢN LÝ\nDÂN CƯ", font=ctk.CTkFont(size=24, weight="bold"), text_color="yellow").pack(pady=30)
        
        self.btn_ds = ctk.CTkButton(self.sidebar, text="Danh sách Hộ Dân", command=self.show_danh_sach, fg_color="#7F1D1D", text_color="white", height=45, anchor="w", font=ctk.CTkFont(size=15, weight="bold"))
        self.btn_ds.pack(fill="x", padx=10, pady=5)
        
        self.btn_tk = ctk.CTkButton(self.sidebar, text="Thống kê Số liệu", command=self.show_thong_ke, fg_color="transparent", text_color="white", height=45, anchor="w", font=ctk.CTkFont(size=15, weight="bold"))
        self.btn_tk.pack(fill="x", padx=10, pady=5)

        # === MAIN CONTENT ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#F3F4F6")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        self.frame_danh_sach = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_thong_ke = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.build_ui_danh_sach()
        self.build_ui_thong_ke()
        
        self.show_danh_sach()
        self.data_source = []
        self.load_data()

    def show_danh_sach(self):
        self.frame_thong_ke.pack_forget()
        self.frame_danh_sach.pack(fill="both", expand=True, padx=20, pady=20)
        self.btn_ds.configure(fg_color="#7F1D1D")
        self.btn_tk.configure(fg_color="transparent")

    def show_thong_ke(self):
        self.frame_danh_sach.pack_forget()
        self.frame_thong_ke.pack(fill="both", expand=True, padx=20, pady=20)
        self.btn_ds.configure(fg_color="transparent")
        self.btn_tk.configure(fg_color="#7F1D1D")
        self.update_thong_ke()

    def build_ui_danh_sach(self):
        top = ctk.CTkFrame(self.frame_danh_sach, fg_color="transparent")
        top.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(top, text="DANH SÁCH HỒ SƠ DÂN CƯ", font=ctk.CTkFont(size=26, weight="bold"), text_color="#1F2937").pack(side="left")
        ctk.CTkButton(top, text="🔄 Tải lại dữ liệu", command=self.load_data, fg_color="#059669", height=40).pack(side="right")

        self.scroll_list = ctk.CTkScrollableFrame(self.frame_danh_sach, fg_color="white", corner_radius=10)
        self.scroll_list.pack(fill="both", expand=True)

    def render_list_items(self):
        for w in self.scroll_list.winfo_children(): w.destroy()
        
        if not self.data_source:
            ctk.CTkLabel(self.scroll_list, text="Đang tải hoặc chưa có dữ liệu...", text_color="gray", font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        for idx, item in enumerate(self.data_source):
            try: mems = json.loads(item.get('danh_sach_thanh_vien', '[]')); count = len(mems) + 1
            except: count = 1
            
            card = ctk.CTkFrame(self.scroll_list, fg_color="#EFF6FF", border_color="#BFDBFE", border_width=1, corner_radius=8)
            card.pack(fill="x", pady=8, padx=10)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=15, pady=15, fill="x", expand=True)
            
            name = str(item.get('ho_ten','')).upper()
            ctk.CTkLabel(info, text=f"{idx+1}. {name}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E40AF", anchor="w").pack(fill="x")
            
            detail_text = f"🏠 {item.get('thuong_tru','')}  |  👨‍👩‍👧‍👦 {count} thành viên"
            if item.get('nguoi_tao_sdt'): detail_text += f"  |  ✍️ Người nhập: {item.get('nguoi_tao_sdt')}"
            
            ctk.CTkLabel(info, text=detail_text, text_color="#4B5563", font=ctk.CTkFont(size=14), anchor="w").pack(fill="x", pady=(5,0))
            
            ctk.CTkButton(card, text="👁️ Xem Chi Tiết", fg_color="#B91C1C", hover_color="#991B1B", width=140, height=40, font=ctk.CTkFont(weight="bold"),
                          command=lambda d=item: self.open_detail_window(d)).pack(side="right", padx=15)

    def open_detail_window(self, data):
        win = ctk.CTkToplevel(self)
        win.title(f"HỒ SƠ: {data.get('ho_ten','').upper()}")
        win.geometry("900x750")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="THÔNG TIN CHI TIẾT", font=ctk.CTkFont(size=22, weight="bold"), text_color="#B91C1C").pack(pady=(20,10))
        scroll = ctk.CTkScrollableFrame(win, fg_color="white", corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Phần I: Chủ hộ
        ctk.CTkLabel(scroll, text="I. CHỦ HỘ", font=ctk.CTkFont(size=18, weight="bold"), text_color="#374151", anchor="w").pack(fill="x", pady=(10,5))
        
        info_grid = ctk.CTkFrame(scroll, fg_color="#F9FAFB", border_color="#E5E7EB", border_width=1)
        info_grid.pack(fill="x", pady=5)

        def add_row(parent, label, value):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=2, padx=10)
            ctk.CTkLabel(row, text=label, width=180, anchor="w", font=ctk.CTkFont(weight="bold", size=14), text_color="#4B5563").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w", font=ctk.CTkFont(size=14), text_color="black").pack(side="left", fill="x", expand=True)
            ctk.CTkFrame(parent, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10)

        # Hiển thị tất cả trường
        fields = [
            ("Họ và tên", "ho_ten"), ("Ngày sinh", "ngay_sinh"), ("Giới tính", "gioi_tinh"),
            ("CMND/CCCD", "so_cmnd"), ("Ngày cấp", "ngay_cap"), ("Nơi cấp", "noi_cap"),
            ("Thường trú", "thuong_tru"), ("Nơi ở hiện tại", "noi_o_hien_tai"), ("Quê quán", "que_quan"),
            ("Dân tộc", "dan_toc"), ("Tôn giáo", "ton_giao"), ("Trình độ", "trinh_do"),
            ("SĐT", "sdt"), ("Công việc", "cong_viec")
        ]
        for lbl, key in fields:
            add_row(info_grid, lbl, data.get(key, ''))

        # Phần II: Thành viên
        try:
            mems = json.loads(data.get('danh_sach_thanh_vien', '[]'))
            if mems:
                ctk.CTkLabel(scroll, text=f"II. THÀNH VIÊN ({len(mems)} người)", font=ctk.CTkFont(size=18, weight="bold"), text_color="#374151", anchor="w").pack(fill="x", pady=(20,5))
                for idx, m in enumerate(mems):
                    mem_card = ctk.CTkFrame(scroll, fg_color="#EFF6FF", border_color="#BFDBFE", border_width=1)
                    mem_card.pack(fill="x", pady=5)
                    head = ctk.CTkFrame(mem_card, fg_color="#DBEAFE", height=30)
                    head.pack(fill="x")
                    ctk.CTkLabel(head, text=f"  #{idx+1} - {m.get('ho_ten','').upper()}", font=ctk.CTkFont(weight="bold"), text_color="#1E40AF").pack(side="left")
                    ctk.CTkLabel(head, text=f"Quan hệ: {m.get('quan_he','')}  ", font=ctk.CTkFont(weight="bold"), text_color="#1E40AF").pack(side="right")
                    
                    info_str = f"Sinh: {m.get('ngay_sinh','')} | CMND: {m.get('so_cmnd','')}\n"
                    info_str += f"Dân tộc: {m.get('dan_toc','')} | Tôn giáo: {m.get('ton_giao','')} | Trình độ: {m.get('trinh_do','')}\n"
                    info_str += f"Công việc: {m.get('cong_viec','')}"
                    tt = m.get('tinh_trang', [])
                    if tt: info_str += " | " + (", ".join(tt) if isinstance(tt, list) else str(tt))
                    
                    ctk.CTkLabel(mem_card, text=info_str, justify="left", anchor="w", text_color="#4B5563").pack(fill="x", padx=10, pady=5)
            else:
                ctk.CTkLabel(scroll, text="II. THÀNH VIÊN: (Không có)", text_color="gray").pack(pady=20)
        except Exception as e: print(e)

        # Footer Button
        footer = ctk.CTkFrame(win, fg_color="white", height=80)
        footer.pack(fill="x", side="bottom")
        ctk.CTkButton(footer, text="🖨️ XUẤT FILE WORD ĐỂ IN", height=50, width=300, 
                      fg_color="#059669", hover_color="#047857", font=ctk.CTkFont(size=16, weight="bold"),
                      command=lambda: self.export_word(data)).pack(pady=15)

    # --- HÀM XUẤT WORD CHUẨN MẪU MỚI ---
    def export_word(self, data):
        template_path = "pc_app/mau_phieu.docx"
        if not os.path.exists(template_path): 
            return messagebox.showerror("Lỗi", "Thiếu file mau_phieu.docx")

        try:
            doc = Document(template_path)
            
            # Mapping khớp 100% với file mẫu của bạn
            mapping = {
                "1. Họ, chữ đệm và tên người khai": data.get('ho_ten', '').upper(),
                "2. Ngày tháng năm sinh": data.get('ngay_sinh', ''),
                "3. Giới tính": data.get('gioi_tinh', ''),
                "4. Địa chỉ thường trú": data.get('thuong_tru', ''),
                "5.Nơi ở hiện tại": data.get('noi_o_hien_tai', ''),
                "6.Số ĐDCN/Số CMND": data.get('so_cmnd', ''),
                "7.Ngày cấp": data.get('ngay_cap', ''),
                "8.Nơi cấp": data.get('noi_cap', ''),
                "9. Quê quán": data.get('que_quan', ''),
                "10.Trình độ văn hoá": data.get('trinh_do', ''),
                "11.Tôn giáo": data.get('ton_giao', ''),
                "12.Dân tộc": data.get('dan_toc', ''),
                "13.SĐT": data.get('sdt', ''),
                "14.Công việc": data.get('cong_viec', '')
            }

            def replace_text_smart(paragraph):
                text = paragraph.text
                for key, val in mapping.items():
                    if key in text:
                        # Regex tìm: Tên trường + (dấu :) + khoảng trắng + (dấu chấm hoặc 3 chấm)
                        # Ví dụ: "3. Giới tính: ..........." -> "3. Giới tính: Nam"
                        # Dùng regex này để chỉ thay thế đoạn dấu chấm ngay sau từ khóa
                        pattern = re.escape(key) + r"(?::)?\s*[.…]{2,}"
                        
                        if val:
                            new_text = re.sub(pattern, f"{key}: {val}", text)
                            if new_text != text:
                                text = new_text
                            else:
                                # Nếu file Word không có dấu chấm (do format lại) thì nối đuôi vào
                                if f"{key}: {val}" not in text:
                                    text = text.replace(key, f"{key}: {val}")
                paragraph.text = text

            # 1. Quét văn bản
            for para in doc.paragraphs:
                replace_text_smart(para)

            # 2. Thêm bảng Thành viên (Chỉ thêm khi có thành viên)
            try:
                mems = json.loads(data.get('danh_sach_thanh_vien', '[]'))
                if len(mems) > 0:
                    doc.add_paragraph("\n") # Cách dòng
                    h = doc.add_paragraph("II. THÔNG TIN NGƯỜI CHUNG HỘ GIA ĐÌNH")
                    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    h.runs[0].bold = True
                    h.runs[0].font.size = Pt(13)
                    
                    # Tạo bảng 6 cột
                    table = doc.add_table(rows=1, cols=6)
                    table.style = 'Table Grid'
                    headers = ["STT", "Họ Tên", "Quan Hệ", "Ngày Sinh", "CMND", "Tình Trạng"]
                    
                    # Header đậm
                    for i, t in enumerate(headers):
                        cell = table.rows[0].cells[i]
                        cell.text = t
                        cell.paragraphs[0].runs[0].bold = True
                    
                    # Dữ liệu
                    for i, m in enumerate(mems):
                        cells = table.add_row().cells
                        cells[0].text = str(i+1)
                        cells[1].text = m.get('ho_ten', '').upper()
                        cells[2].text = m.get('quan_he', '')
                        cells[3].text = m.get('ngay_sinh', '')
                        cells[4].text = m.get('so_cmnd', '')
                        tt = m.get('tinh_trang', [])
                        cells[5].text = ", ".join(tt) if isinstance(tt, list) else str(tt)

            except Exception as e: print("Lỗi xuất thành viên:", e)

            # Lưu file
            filename = f"Phieu_{data.get('ho_ten','Noname')}.docx"
            path = filedialog.asksaveasfilename(defaultextension=".docx", initialfile=filename)
            if path:
                doc.save(path)
                os.startfile(path) # Mở file luôn
                messagebox.showinfo("Thành công", "Đã xuất file Word chuẩn mẫu!")

        except Exception as e: messagebox.showerror("Lỗi", str(e))

    def build_ui_thong_ke(self):
        ctk.CTkLabel(self.frame_thong_ke, text="THỐNG KÊ SỐ LIỆU", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=20)
        self.stats_container = ctk.CTkFrame(self.frame_thong_ke, fg_color="transparent")
        self.stats_container.pack(fill="both", expand=True)

    def update_thong_ke(self):
        for w in self.stats_container.winfo_children(): w.destroy()
        if not self.data_source: return
        
        total_ho = len(self.data_source)
        total_nguoi = 0
        addr_map = {}

        for item in self.data_source:
            try: total_nguoi += 1 + len(json.loads(item.get('danh_sach_thanh_vien','[]')))
            except: total_nguoi += 1
            addr = item.get('thuong_tru', 'Chưa rõ')
            addr_map[addr] = addr_map.get(addr, 0) + 1

        row1 = ctk.CTkFrame(self.stats_container, fg_color="transparent")
        row1.pack(fill="x", pady=10)
        def card(p, t, v, c):
            f = ctk.CTkFrame(p, fg_color=c, height=120, corner_radius=10)
            f.pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkLabel(f, text=t, text_color="white", font=ctk.CTkFont(size=14)).pack(pady=20)
            ctk.CTkLabel(f, text=str(v), text_color="white", font=ctk.CTkFont(size=36, weight="bold")).pack()

        card(row1, "TỔNG SỐ HỘ", total_ho, "#059669")
        card(row1, "TỔNG NHÂN KHẨU", total_nguoi, "#2563EB")
        
        ctk.CTkLabel(self.stats_container, text="CHI TIẾT ĐỊA BÀN", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=20)
        scroll = ctk.CTkScrollableFrame(self.stats_container, fg_color="white", height=300)
        scroll.pack(fill="x")
        for addr, cnt in addr_map.items():
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=5)
            ctk.CTkLabel(r, text=addr).pack(side="left", padx=10)
            ctk.CTkLabel(r, text=f"{cnt} hộ", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

    def load_data(self):
        def task():
            try:
                res = requests.get(f"{API_URL}/danh-sach", timeout=60)
                if res.status_code==200:
                    self.data_source = res.json()
                    self.after(0, self.render_list_items)
                else: self.after(0, lambda: messagebox.showerror("Lỗi", "Lỗi tải"))
            except: self.after(0, lambda: messagebox.showerror("Lỗi", "Không kết nối được Server"))
        threading.Thread(target=task).start()

if __name__ == "__main__":
    app = AppQuanLyDanCu()
    app.mainloop()