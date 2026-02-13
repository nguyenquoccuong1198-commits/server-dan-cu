import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, 
  ScrollView, Alert, ActivityIndicator, SafeAreaView, StatusBar, KeyboardAvoidingView, Platform 
} from 'react-native';

// ⚠️ THAY LINK RENDER CỦA BẠN VÀO ĐÂY
const API_URL = 'https://api-dan-cu.onrender.com/api'; 

export default function App() {
  const [loading, setLoading] = useState(false);
  
  // Quản lý dữ liệu form (Theo file Word)
  const [form, setForm] = useState({
    ho_ten: '', ngay_sinh: '', gio_tinh: 'Nam',
    thuong_tru: '', noi_o_hien_tai: '',
    so_cmnd: '', ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH',
    que_quan: '', dan_toc: 'Kinh', ton_giao: 'Không',
    sdt: '', nghe_nghiep: 'Đang có việc làm'
  });

  const updateForm = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const guiPhieu = async () => {
    if (!form.ho_ten || !form.sdt) {
      Alert.alert("Thiếu thông tin", "Vui lòng nhập ít nhất Họ tên và SĐT");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/gui-phieu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (response.ok) {
        Alert.alert("Thành công", "✅ Đã gửi phiếu rà soát lên hệ thống!");
        // Reset form (giữ lại các trường mặc định cho nhanh)
        setForm({
          ...form, ho_ten: '', sdt: '', so_cmnd: '', 
          ngay_sinh: '', thuong_tru: '', noi_o_hien_tai: ''
        });
      } else {
        Alert.alert("Lỗi", "Server không nhận phiếu.");
      }
    } catch (error) {
      Alert.alert("Lỗi Mạng", "Không thể kết nối Server.");
    } finally {
      setLoading(false);
    }
  };

  // Component chọn (Radio Button)
  const RadioOption = ({ label, value, selectedValue, onSelect }) => (
    <TouchableOpacity 
      style={[styles.radio, selectedValue === value && styles.radioSelected]} 
      onPress={() => onSelect(value)}
    >
      <Text style={[styles.radioText, selectedValue === value && styles.radioTextSelected]}>{label}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#B91C1C" />
      
      {/* HEADER: Màu đỏ theo phong cách giấy tờ hành chính */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>PHIẾU RÀ SOÁT</Text>
        <Text style={styles.headerSubtitle}>THÔNG TIN HỘ DÂN (Lưu hành nội bộ)</Text>
      </View>

      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{flex: 1}}>
      <ScrollView contentContainerStyle={styles.body}>
        
        {/* PHẦN I: ĐẠI DIỆN NGƯỜI KHAI */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>I. THÔNG TIN NGƯỜI KHAI</Text>
          
          <Text style={styles.label}>1. Họ và tên người khai (*)</Text>
          <TextInput style={styles.input} placeholder="NHẬP CHỮ IN HOA" value={form.ho_ten} onChangeText={t => updateForm('ho_ten', t.toUpperCase())} />

          <View style={styles.row}>
            <View style={{flex: 1, marginRight: 10}}>
              <Text style={styles.label}>2. Ngày sinh</Text>
              <TextInput style={styles.input} placeholder="dd/mm/yyyy" value={form.ngay_sinh} onChangeText={t => updateForm('ngay_sinh', t)} />
            </View>
            <View style={{flex: 1}}>
              <Text style={styles.label}>3. Giới tính</Text>
              <View style={{flexDirection: 'row'}}>
                <RadioOption label="Nam" value="Nam" selectedValue={form.gio_tinh} onSelect={v => updateForm('gio_tinh', v)} />
                <View style={{width: 5}} />
                <RadioOption label="Nữ" value="Nữ" selectedValue={form.gio_tinh} onSelect={v => updateForm('gio_tinh', v)} />
              </View>
            </View>
          </View>

          <Text style={styles.label}>4. Địa chỉ thường trú</Text>
          <TextInput style={styles.input} placeholder="Xã/Phường, Quận/Huyện..." value={form.thuong_tru} onChangeText={t => updateForm('thuong_tru', t)} />

          <Text style={styles.label}>5. Nơi ở hiện tại (Nếu khác thường trú)</Text>
          <TextInput style={styles.input} placeholder="Nhập địa chỉ hiện tại..." value={form.noi_o_hien_tai} onChangeText={t => updateForm('noi_o_hien_tai', t)} />

          <View style={styles.row}>
             <View style={{flex: 1.5, marginRight: 10}}>
                <Text style={styles.label}>6. Số CMND/CCCD</Text>
                <TextInput style={styles.input} keyboardType="numeric" value={form.so_cmnd} onChangeText={t => updateForm('so_cmnd', t)} />
             </View>
             <View style={{flex: 1}}>
                <Text style={styles.label}>7. Ngày cấp</Text>
                <TextInput style={styles.input} placeholder="dd/mm/yyyy" value={form.ngay_cap} onChangeText={t => updateForm('ngay_cap', t)} />
             </View>
          </View>

          <Text style={styles.label}>8. Quê quán</Text>
          <TextInput style={styles.input} value={form.que_quan} onChangeText={t => updateForm('que_quan', t)} />

          <View style={styles.row}>
            <View style={{flex: 1, marginRight: 10}}>
              <Text style={styles.label}>13. Dân tộc</Text>
              <TextInput style={styles.input} value={form.dan_toc} onChangeText={t => updateForm('dan_toc', t)} />
            </View>
            <View style={{flex: 1}}>
              <Text style={styles.label}>14. SĐT (*)</Text>
              <TextInput style={styles.input} keyboardType="phone-pad" value={form.sdt} onChangeText={t => updateForm('sdt', t)} />
            </View>
          </View>

          <Text style={styles.label}>15. Công việc hiện tại</Text>
          <View style={{flexDirection: 'row', flexWrap: 'wrap', marginBottom: 10}}>
             {['Thất nghiệp', 'Đang có việc làm', 'Hưu trí', 'Học sinh'].map((job) => (
                <TouchableOpacity 
                  key={job}
                  style={[styles.chip, form.nghe_nghiep === job && styles.chipSelected]}
                  onPress={() => updateForm('nghe_nghiep', job)}
                >
                  <Text style={[styles.chipText, form.nghe_nghiep === job && styles.chipTextSelected]}>{job}</Text>
                </TouchableOpacity>
             ))}
          </View>
        </View>

        {/* NÚT GỬI */}
        <TouchableOpacity style={styles.submitButton} onPress={guiPhieu} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitText}>GỬI PHIẾU KHẢO SÁT</Text>}
        </TouchableOpacity>

        <View style={{height: 50}} /> 
      </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  header: {
    backgroundColor: '#B91C1C', padding: 20, paddingTop: 40, alignItems: 'center',
    shadowColor: "#000", shadowOpacity: 0.3, elevation: 5
  },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#fff', textTransform: 'uppercase' },
  headerSubtitle: { fontSize: 13, color: '#FECACA', marginTop: 4, fontStyle: 'italic' },
  body: { padding: 15 },
  section: { backgroundColor: '#fff', borderRadius: 10, padding: 15, marginBottom: 20, elevation: 2 },
  sectionHeader: { fontSize: 16, fontWeight: 'bold', color: '#B91C1C', marginBottom: 15, borderBottomWidth: 1, borderBottomColor: '#eee', paddingBottom: 5 },
  label: { fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 10 },
  input: {
    backgroundColor: '#F9FAFB', borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 6,
    padding: 10, fontSize: 15, color: '#111827'
  },
  row: { flexDirection: 'row', alignItems: 'center' },
  radio: {
    flex: 1, borderWidth: 1, borderColor: '#D1D5DB', padding: 10, borderRadius: 6, alignItems: 'center', backgroundColor: '#F9FAFB'
  },
  radioSelected: { backgroundColor: '#FEF2F2', borderColor: '#B91C1C' },
  radioText: { color: '#6B7280' },
  radioTextSelected: { color: '#B91C1C', fontWeight: 'bold' },
  chip: {
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#E5E7EB',
    marginRight: 8, marginBottom: 8, backgroundColor: '#F3F4F6'
  },
  chipSelected: { backgroundColor: '#B91C1C', borderColor: '#B91C1C' },
  chipText: { fontSize: 12, color: '#4B5563' },
  chipTextSelected: { color: '#fff', fontWeight: 'bold' },
  submitButton: {
    backgroundColor: '#B91C1C', padding: 16, borderRadius: 8, alignItems: 'center',
    shadowColor: "#B91C1C", shadowOpacity: 0.4, elevation: 4
  },
  submitText: { color: '#fff', fontSize: 18, fontWeight: 'bold', textTransform: 'uppercase' }
});