import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, 
  Alert, SafeAreaView, StatusBar, KeyboardAvoidingView, Platform, Switch
} from 'react-native';

const API_URL = 'https://api-dan-cu.onrender.com/api'; 

export default function App() {
  const [activeTab, setActiveTab] = useState(1); // 1: Đại diện, 2: Thành viên
  const [loading, setLoading] = useState(false);

  // Dữ liệu Tab 1: Người đại diện
  const [nguoiKhai, setNguoiKhai] = useState({
    ho_ten: '', ngay_sinh: '', gio_tinh: 'Nam',
    so_cmnd: '', ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH - BCA',
    thuong_tru: '', noi_o_hien_tai: '',
    que_quan: '', trinh_do: '12/12', dan_toc: 'Kinh', ton_giao: 'Không',
    sdt: '', cong_viec: 'Đang có việc làm'
  });

  // Dữ liệu Tab 2: Danh sách thành viên
  const [thanhVien, setThanhVien] = useState([]);

  // --- LOGIC XỬ LÝ ---
  const updateNguoiKhai = (key, value) => {
    setNguoiKhai(prev => ({ ...prev, [key]: value }));
  };

  const themThanhVien = () => {
    setThanhVien([...thanhVien, {
      ho_ten: '', quan_he: 'Con', ngay_sinh: '', so_cmnd: '', 
      ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH - BCA',
      thuong_tru: '', noi_o_hien_tai: '',
      trinh_do: '', chuyen_mon: '', dan_toc: 'Kinh', ton_giao: 'Không', quoc_tich: 'Việt Nam',
      sdt: '', tinh_trang: [] // Mảng lưu các checkbox
    }]);
  };

  const xoaThanhVien = (index) => {
    const newList = [...thanhVien];
    newList.splice(index, 1);
    setThanhVien(newList);
  };

  const updateThanhVien = (index, key, value) => {
    const newList = [...thanhVien];
    newList[index][key] = value;
    
    // Logic cảnh báo sống một mình
    if (key === 'tinh_trang' && value.includes('Sống Một Mình')) {
       Alert.alert("Cảnh báo", "Bạn đang khai báo hộ gia đình. Nếu chọn 'Sống một mình', vui lòng kiểm tra lại xem có mâu thuẫn không?");
    }
    setThanhVien(newList);
  };

  const copyDiaChiTuChuHo = (index) => {
    if (!nguoiKhai.thuong_tru && !nguoiKhai.noi_o_hien_tai) {
      Alert.alert("Thông báo", "Vui lòng nhập địa chỉ Chủ hộ ở Tab 1 trước!");
      return;
    }
    const newList = [...thanhVien];
    newList[index].thuong_tru = nguoiKhai.thuong_tru;
    newList[index].noi_o_hien_tai = nguoiKhai.noi_o_hien_tai;
    setThanhVien(newList);
    Alert.alert("Đã sao chép", "Đã điền địa chỉ của chủ hộ vào thành viên này.");
  };

  const guiHoSo = async () => {
    // Validation cơ bản
    if (!nguoiKhai.ho_ten || !nguoiKhai.sdt || !nguoiKhai.so_cmnd) {
      Alert.alert("Thiếu thông tin", "Tab 1: Vui lòng nhập Họ tên, CMND và SĐT.");
      return;
    }
    if (nguoiKhai.so_cmnd.length !== 9 && nguoiKhai.so_cmnd.length !== 12) {
       Alert.alert("Sai định dạng", "Số CMND/CCCD phải là 9 hoặc 12 số.");
       return;
    }

    setLoading(true);
    const data = {
      ...nguoiKhai,
      danh_sach_thanh_vien: JSON.stringify(thanhVien) // Chuyển danh sách thành chuỗi để gửi
    };

    try {
      const response = await fetch(`${API_URL}/gui-phieu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        Alert.alert("Thành công", "✅ Đã lưu hồ sơ hộ dân!");
        // Reset
        setNguoiKhai({
            ho_ten: '', ngay_sinh: '', gio_tinh: 'Nam', so_cmnd: '', ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH - BCA',
            thuong_tru: '', noi_o_hien_tai: '', que_quan: '', trinh_do: '12/12', dan_toc: 'Kinh', ton_giao: 'Không',
            sdt: '', cong_viec: 'Đang có việc làm'
        });
        setThanhVien([]);
        setActiveTab(1);
      } else {
        Alert.alert("Lỗi", "Server không nhận dữ liệu.");
      }
    } catch (e) {
      Alert.alert("Lỗi mạng", "Không kết nối được Server.");
    } finally {
      setLoading(false);
    }
  };

  // --- COMPONENT CON ---
  const InputField = ({ label, val, setVal, placeholder, keyboard = 'default' }) => (
    <View style={styles.inputGroup}>
      <Text style={styles.label}>{label}</Text>
      <TextInput 
        style={styles.input} value={val} onChangeText={setVal} 
        placeholder={placeholder} keyboardType={keyboard} 
      />
    </View>
  );

  const RadioGroup = ({ label, options, selected, onSelect }) => (
    <View style={styles.inputGroup}>
      <Text style={styles.label}>{label}</Text>
      <View style={{flexDirection: 'row', flexWrap: 'wrap'}}>
        {options.map(opt => (
          <TouchableOpacity 
            key={opt} 
            style={[styles.radioBtn, selected === opt && styles.radioSelected]}
            onPress={() => onSelect(opt)}
          >
            <Text style={[styles.radioText, selected === opt && styles.textSelected]}>{opt}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#B91C1C" />
      
      {/* HEADER */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>HỒ SƠ DÂN CƯ ĐIỆN TỬ</Text>
      </View>

      {/* TABS BUTTON */}
      <View style={styles.tabContainer}>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 1 && styles.tabActive]} onPress={() => setActiveTab(1)}>
          <Text style={[styles.tabText, activeTab === 1 && styles.textSelected]}>1. NGƯỜI ĐẠI DIỆN</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 2 && styles.tabActive]} onPress={() => setActiveTab(2)}>
          <Text style={[styles.tabText, activeTab === 2 && styles.textSelected]}>2. THÀNH VIÊN ({thanhVien.length})</Text>
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{flex: 1}}>
        <ScrollView contentContainerStyle={styles.body}>
          
          {/* === TAB 1: NGƯỜI KHAI === */}
          {activeTab === 1 && (
            <View>
              <InputField label="Họ và tên người khai (*)" val={nguoiKhai.ho_ten} setVal={t => updateNguoiKhai('ho_ten', t.toUpperCase())} placeholder="NHẬP CHỮ IN HOA" />
              <View style={styles.row}>
                 <View style={{flex: 1, marginRight: 5}}><InputField label="Ngày sinh (dd/mm/yyyy)" val={nguoiKhai.ngay_sinh} setVal={t => updateNguoiKhai('ngay_sinh', t)} /></View>
                 <View style={{flex: 1}}><RadioGroup label="Giới tính" options={['Nam', 'Nữ']} selected={nguoiKhai.gioi_tinh} onSelect={v => updateNguoiKhai('gio_tinh', v)} /></View>
              </View>
              <InputField label="Số CMND/CCCD (*)" val={nguoiKhai.so_cmnd} setVal={t => updateNguoiKhai('so_cmnd', t)} keyboard="numeric" />
              <View style={styles.row}>
                 <View style={{flex: 1, marginRight: 5}}><InputField label="Ngày cấp" val={nguoiKhai.ngay_cap} setVal={t => updateNguoiKhai('ngay_cap', t)} /></View>
                 <View style={{flex: 1}}><InputField label="Nơi cấp" val={nguoiKhai.noi_cap} setVal={t => updateNguoiKhai('noi_cap', t)} /></View>
              </View>
              
              <InputField label="Địa chỉ thường trú" val={nguoiKhai.thuong_tru} setVal={t => updateNguoiKhai('thuong_tru', t)} />
              
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Nơi ở hiện tại</Text>
                <TextInput style={styles.input} value={nguoiKhai.noi_o_hien_tai} onChangeText={t => updateNguoiKhai('noi_o_hien_tai', t)} />
                <TouchableOpacity onPress={() => updateNguoiKhai('noi_o_hien_tai', nguoiKhai.thuong_tru)}>
                    <Text style={{color: '#B91C1C', marginTop: 5, fontWeight: 'bold'}}>⬇️ Giống thường trú</Text>
                </TouchableOpacity>
              </View>

              <InputField label="Quê quán" val={nguoiKhai.que_quan} setVal={t => updateNguoiKhai('que_quan', t)} />
              <View style={styles.row}>
                <View style={{flex: 1, marginRight: 5}}><InputField label="Dân tộc" val={nguoiKhai.dan_toc} setVal={t => updateNguoiKhai('dan_toc', t)} /></View>
                <View style={{flex: 1}}><InputField label="Tôn giáo" val={nguoiKhai.ton_giao} setVal={t => updateNguoiKhai('ton_giao', t)} /></View>
              </View>
              <InputField label="Trình độ văn hóa" val={nguoiKhai.trinh_do} setVal={t => updateNguoiKhai('trinh_do', t)} />
              <InputField label="Số điện thoại (*)" val={nguoiKhai.sdt} setVal={t => updateNguoiKhai('sdt', t)} keyboard="phone-pad" />
              
              <RadioGroup 
                label="Công việc hiện tại" 
                options={['Thất nghiệp', 'Đang có việc làm', 'Hết tuổi lao động', 'Học sinh']} 
                selected={nguoiKhai.cong_viec} onSelect={v => updateNguoiKhai('cong_viec', v)} 
              />
              
              <TouchableOpacity style={styles.nextBtn} onPress={() => setActiveTab(2)}>
                  <Text style={styles.nextText}>TIẾP TỤC: NHẬP THÀNH VIÊN 👉</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* === TAB 2: THÀNH VIÊN === */}
          {activeTab === 2 && (
            <View>
              {thanhVien.map((tv, index) => (
                <View key={index} style={styles.memberCard}>
                  <View style={{flexDirection: 'row', justifyContent: 'space-between'}}>
                      <Text style={styles.memberTitle}>Thành viên #{index + 1}</Text>
                      <TouchableOpacity onPress={() => xoaThanhVien(index)}><Text style={{color: 'red'}}>🗑 Xóa</Text></TouchableOpacity>
                  </View>
                  
                  <InputField label="Họ và tên" val={tv.ho_ten} setVal={t => updateThanhVien(index, 'ho_ten', t.toUpperCase())} />
                  <InputField label="Quan hệ với chủ hộ" val={tv.quan_he} setVal={t => updateThanhVien(index, 'quan_he', t)} placeholder="Vợ/Chồng/Con..." />
                  
                  <View style={styles.row}>
                    <View style={{flex: 1, marginRight: 5}}><InputField label="Ngày sinh" val={tv.ngay_sinh} setVal={t => updateThanhVien(index, 'ngay_sinh', t)} /></View>
                    <View style={{flex: 1}}><InputField label="CMND/ĐDCN" val={tv.so_cmnd} setVal={t => updateThanhVien(index, 'so_cmnd', t)} keyboard="numeric"/></View>
                  </View>
                  
                  <TouchableOpacity style={styles.copyBtn} onPress={() => copyDiaChiTuChuHo(index)}>
                     <Text style={{color: '#fff'}}>📋 Sao chép địa chỉ từ Chủ Hộ</Text>
                  </TouchableOpacity>
                  
                  <InputField label="Địa chỉ thường trú" val={tv.thuong_tru} setVal={t => updateThanhVien(index, 'thuong_tru', t)} />
                  <InputField label="Nơi ở hiện tại" val={tv.noi_o_hien_tai} setVal={t => updateThanhVien(index, 'noi_o_hien_tai', t)} />
                  
                  <InputField label="Chuyên môn" val={tv.chuyen_mon} setVal={t => updateThanhVien(index, 'chuyen_mon', t)} />
                  <InputField label="Quốc tịch" val={tv.quoc_tich} setVal={t => updateThanhVien(index, 'quoc_tich', t)} />
                  
                  <Text style={styles.label}>Tình trạng (Chọn nhiều):</Text>
                  <View style={{flexDirection: 'row', flexWrap: 'wrap'}}>
                      {['Thất nghiệp', 'Đang có việc làm', 'Hết tuổi lao động', 'Học sinh', 'Trẻ sơ sinh', 'Sống Một Mình'].map(tt => (
                          <TouchableOpacity 
                            key={tt}
                            style={[styles.checkbox, tv.tinh_trang.includes(tt) && styles.checkboxSelected]}
                            onPress={() => {
                                const current = tv.tinh_trang;
                                const newVal = current.includes(tt) ? current.filter(i => i !== tt) : [...current, tt];
                                updateThanhVien(index, 'tinh_trang', newVal);
                            }}
                          >
                             <Text style={tv.tinh_trang.includes(tt) ? styles.textSelected : {color: '#333'}}>{tt}</Text>
                          </TouchableOpacity>
                      ))}
                  </View>
                </View>
              ))}

              <TouchableOpacity style={styles.addBtn} onPress={themThanhVien}>
                 <Text style={styles.addText}>+ THÊM THÀNH VIÊN</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.submitBtn} onPress={guiHoSo} disabled={loading}>
                 <Text style={styles.submitText}>{loading ? "ĐANG GỬI..." : "GỬI TOÀN BỘ HỒ SƠ"}</Text>
              </TouchableOpacity>
            </View>
          )}
          
          <View style={{height: 100}} /> 
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  header: { backgroundColor: '#B91C1C', padding: 20, paddingTop: 40, alignItems: 'center' },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#fff' },
  tabContainer: { flexDirection: 'row', backgroundColor: '#fff' },
  tabBtn: { flex: 1, padding: 15, alignItems: 'center', borderBottomWidth: 3, borderBottomColor: 'transparent' },
  tabActive: { borderBottomColor: '#B91C1C' },
  tabText: { fontWeight: 'bold', color: '#6B7280' },
  textSelected: { color: '#B91C1C' },
  body: { padding: 15 },
  inputGroup: { marginBottom: 15 },
  label: { fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 5 },
  input: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 6, padding: 10, fontSize: 15 },
  row: { flexDirection: 'row' },
  radioBtn: { paddingHorizontal: 10, paddingVertical: 6, borderWidth: 1, borderColor: '#ccc', borderRadius: 20, marginRight: 8, marginBottom: 8 },
  radioSelected: { borderColor: '#B91C1C', backgroundColor: '#FEF2F2' },
  radioText: { fontSize: 13 },
  nextBtn: { backgroundColor: '#4B5563', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 20 },
  nextText: { color: '#fff', fontWeight: 'bold' },
  // Tab 2 styles
  memberCard: { backgroundColor: '#fff', padding: 10, borderRadius: 8, marginBottom: 15, borderLeftWidth: 4, borderLeftColor: '#B91C1C', elevation: 2 },
  memberTitle: { fontWeight: 'bold', color: '#B91C1C', marginBottom: 10 },
  copyBtn: { backgroundColor: '#059669', padding: 8, borderRadius: 5, alignItems: 'center', marginVertical: 10 },
  addBtn: { borderWidth: 1, borderColor: '#B91C1C', padding: 15, borderRadius: 8, alignItems: 'center', borderStyle: 'dashed', marginBottom: 10 },
  addText: { color: '#B91C1C', fontWeight: 'bold' },
  submitBtn: { backgroundColor: '#B91C1C', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  submitText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  checkbox: { padding: 8, borderWidth: 1, borderColor: '#ccc', borderRadius: 4, marginRight: 8, marginBottom: 8 },
  checkboxSelected: { backgroundColor: '#FEF2F2', borderColor: '#B91C1C' }
});