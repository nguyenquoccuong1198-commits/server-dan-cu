import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, 
  Alert, SafeAreaView, StatusBar, KeyboardAvoidingView, Platform
} from 'react-native';

const API_URL = 'https://api-dan-cu.onrender.com/api'; 

// --- 1. COMPONENT INPUT ---
const InputField = ({ label, val, setVal, placeholder, keyboard = 'default', isPassword=false }) => (
  <View style={styles.inputGroup}>
    <Text style={styles.label}>{label}</Text>
    <TextInput 
      style={styles.input} value={val} onChangeText={setVal} 
      placeholder={placeholder} keyboardType={keyboard} secureTextEntry={isPassword}
    />
  </View>
);

// --- 2. COMPONENT RADIO ---
const RadioGroup = ({ label, options, selected, onSelect }) => (
  <View style={styles.inputGroup}>
    <Text style={styles.label}>{label}</Text>
    <View style={{flexDirection: 'row', flexWrap: 'wrap'}}>
      {options.map(opt => (
        <TouchableOpacity 
          key={opt} 
          style={[styles.radioBtn, selected === opt && styles.radioSelected]}
          onPress={() => onSelect(opt)}
          activeOpacity={0.7}
        >
          <View style={[styles.radioCircle, selected === opt && styles.radioCircleSelected]} />
          <Text style={[styles.radioText, selected === opt && styles.textSelected]}>{opt}</Text>
        </TouchableOpacity>
      ))}
    </View>
  </View>
);

// --- 3. MÀN HÌNH ĐĂNG NHẬP ---
const LoginScreen = ({ onLoginSuccess, onGoRegister }) => {
  const [phone, setPhone] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if(!phone || !pass) return Alert.alert("Lỗi", "Nhập đủ thông tin");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/dang-nhap`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ sdt: phone, mat_khau: pass })
      });
      const data = await res.json();
      if(res.ok) { 
        // Server giờ đã trả về đúng tên người đăng ký
        onLoginSuccess({ sdt: phone, ho_ten: data.ho_ten }); 
      } else { Alert.alert("Thất bại", data.detail); }
    } catch { Alert.alert("Lỗi mạng", "Không kết nối được Server"); }
    setLoading(false);
  };

  return (
    <View style={styles.authContainer}>
      <StatusBar barStyle="light-content" backgroundColor="#B91C1C" />
      <View style={styles.logoBox}><Text style={styles.logoText}>VNeID</Text><Text style={styles.logoSub}>QUẢN LÝ DÂN CƯ ĐỊA PHƯƠNG</Text></View>
      <View style={styles.authBox}>
        <Text style={styles.authTitle}>ĐĂNG NHẬP</Text>
        <TextInput style={styles.authInput} placeholder="SĐT" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
        <TextInput style={styles.authInput} placeholder="Mật khẩu" secureTextEntry value={pass} onChangeText={setPass} />
        <TouchableOpacity style={styles.authBtn} onPress={handleLogin} disabled={loading}><Text style={styles.authBtnText}>{loading ? "..." : "ĐĂNG NHẬP"}</Text></TouchableOpacity>
        <TouchableOpacity onPress={onGoRegister} style={{marginTop: 20}}><Text style={{color: '#B91C1C', fontWeight: 'bold'}}>Đăng ký tài khoản mới</Text></TouchableOpacity>
      </View>
    </View>
  );
};

// --- 4. MÀN HÌNH ĐĂNG KÝ ---
const RegisterScreen = ({ onGoLogin }) => {
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if(!phone || !pass || !name) return Alert.alert("Lỗi", "Nhập đủ thông tin");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/dang-ky`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ sdt: phone, mat_khau: pass, ho_ten: name })
      });
      if(res.ok) { Alert.alert("Thành công", "Đăng ký xong! Hãy đăng nhập."); onGoLogin(); } 
      else { const d = await res.json(); Alert.alert("Lỗi", d.detail); }
    } catch { Alert.alert("Lỗi mạng", "Không kết nối được Server"); }
    setLoading(false);
  };

  return (
    <View style={styles.authContainer}>
      <View style={styles.logoBox}><Text style={styles.logoText}>ĐĂNG KÝ</Text></View>
      <View style={styles.authBox}>
        <TextInput style={styles.authInput} placeholder="Họ tên hiển thị" value={name} onChangeText={setName} />
        <TextInput style={styles.authInput} placeholder="SĐT" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
        <TextInput style={styles.authInput} placeholder="Mật khẩu" secureTextEntry value={pass} onChangeText={setPass} />
        <TouchableOpacity style={styles.authBtn} onPress={handleRegister} disabled={loading}><Text style={styles.authBtnText}>{loading ? "..." : "ĐĂNG KÝ"}</Text></TouchableOpacity>
        <TouchableOpacity onPress={onGoLogin} style={{marginTop: 20}}><Text style={{color: '#B91C1C', fontWeight: 'bold'}}>Quay lại đăng nhập</Text></TouchableOpacity>
      </View>
    </View>
  );
};

// --- 5. MAIN FORM ---
const MainForm = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // Dữ liệu Người khai 
  const [nguoiKhai, setNguoiKhai] = useState({
    ho_ten: '', ngay_sinh: '', 
    gioi_tinh: 'Nam', // ĐÃ SỬA: 'gioi_tinh' (có chữ i) để khớp Server
    so_cmnd: '', ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH - BCA',
    thuong_tru: '', noi_o_hien_tai: '', 
    que_quan: '', trinh_do: '12/12', dan_toc: 'Kinh', ton_giao: 'Không',
    sdt: '', cong_viec: 'Đang có việc làm'
  });
  
  const [thanhVien, setThanhVien] = useState([]);

  // Logic cập nhật (Đã sửa key gioi_tinh)
  const updateNguoiKhai = (k, v) => setNguoiKhai(prev => ({ ...prev, [k]: v }));
  
  const themThanhVien = () => setThanhVien([...thanhVien, {
    ho_ten: '', quan_he: 'Con', ngay_sinh: '', 
    so_cmnd: '', ngay_cap: '', noi_cap: 'Cục CS QLHC về TTXH - BCA',
    thuong_tru: '', noi_o_hien_tai: '', 
    trinh_do: '', chuyen_mon: '', dan_toc: 'Kinh', ton_giao: 'Không', quoc_tich: 'Việt Nam',
    sdt: '', cong_viec: '', tinh_trang: [] 
  }]);
  
  const xoaThanhVien = (i) => { const n = [...thanhVien]; n.splice(i, 1); setThanhVien(n); };
  
  const updateThanhVien = (i, k, v) => {
    const n = [...thanhVien]; n[i][k] = v;
    if (k === 'tinh_trang' && v.includes('Sống Một Mình')) Alert.alert("Cảnh báo", "Đang khai hộ gia đình, sao lại Sống một mình?");
    setThanhVien(n);
  };

  const copyDiaChi = (i) => {
    if(!nguoiKhai.thuong_tru) return Alert.alert("Lỗi", "Nhập địa chỉ chủ hộ trước");
    const n = [...thanhVien]; n[i].thuong_tru = nguoiKhai.thuong_tru; n[i].noi_o_hien_tai = nguoiKhai.noi_o_hien_tai;
    setThanhVien(n); Alert.alert("Xong", "Đã sao chép");
  };

  const guiHoSo = async () => {
    if(!nguoiKhai.ho_ten || !nguoiKhai.so_cmnd) return Alert.alert("Thiếu", "Nhập tên và CMND");
    setLoading(true);
    // Gửi kèm gioi_tinh đã sửa
    const data = { ...nguoiKhai, danh_sach_thanh_vien: JSON.stringify(thanhVien), nguoi_tao_sdt: user.sdt };
    try {
      const res = await fetch(`${API_URL}/gui-phieu`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)});
      if(res.ok) {
        Alert.alert("Thành công", "✅ Đã gửi phiếu!");
        setNguoiKhai({ ho_ten:'', ngay_sinh:'', gioi_tinh:'Nam', so_cmnd:'', ngay_cap:'', noi_cap:'Cục CS QLHC về TTXH - BCA', thuong_tru:'', noi_o_hien_tai:'', que_quan:'', trinh_do:'12/12', dan_toc:'Kinh', ton_giao:'Không', sdt:'', cong_viec:'Đang có việc làm'});
        setThanhVien([]); setActiveTab(1);
      } else { Alert.alert("Lỗi", "Server từ chối"); }
    } catch { Alert.alert("Lỗi mạng", "Kiểm tra kết nối"); }
    setLoading(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#B91C1C" />
      <View style={styles.header}>
        {/* HIỆN ĐÚNG TÊN NGƯỜI DÙNG */}
        <Text style={styles.headerTitle}>XIN CHÀO: {user.ho_ten ? user.ho_ten.toUpperCase() : user.sdt}</Text>
        <TouchableOpacity onPress={onLogout}><Text style={{color:'#fff', textDecorationLine:'underline'}}>Đăng xuất</Text></TouchableOpacity>
      </View>
      
      <View style={styles.tabContainer}>
        <TouchableOpacity style={[styles.tabBtn, activeTab===1 && styles.tabActive]} onPress={()=>setActiveTab(1)}><Text style={[styles.tabText, activeTab===1 && styles.textSelected]}>1. ĐẠI DIỆN</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab===2 && styles.tabActive]} onPress={()=>setActiveTab(2)}><Text style={[styles.tabText, activeTab===2 && styles.textSelected]}>2. THÀNH VIÊN ({thanhVien.length})</Text></TouchableOpacity>
      </View>

      <KeyboardAvoidingView behavior={Platform.OS==="ios"?"padding":"height"} style={{flex:1}}>
        <ScrollView contentContainerStyle={styles.body} keyboardShouldPersistTaps="handled">
          {activeTab === 1 && (
            <View>
              <InputField label="Họ tên người khai (*)" val={nguoiKhai.ho_ten} setVal={v=>updateNguoiKhai('ho_ten', v.toUpperCase())} placeholder="IN HOA" />
              <View style={styles.row}>
                  <View style={{flex:1, marginRight:5}}><InputField label="Ngày sinh" val={nguoiKhai.ngay_sinh} setVal={v=>updateNguoiKhai('ngay_sinh', v)}/></View>
                  {/* COMPONENT RADIO ĐÃ DÙNG ĐÚNG BIẾN 'gioi_tinh' */}
                  <View style={{flex:1}}><RadioGroup label="Giới tính" options={['Nam','Nữ']} selected={nguoiKhai.gioi_tinh} onSelect={v=>updateNguoiKhai('gioi_tinh',v)}/></View>
              </View>
              <InputField label="CMND/CCCD (*)" val={nguoiKhai.so_cmnd} setVal={v=>updateNguoiKhai('so_cmnd',v)} keyboard="numeric"/>
              <View style={styles.row}>
                  <View style={{flex:1, marginRight:5}}><InputField label="Ngày cấp" val={nguoiKhai.ngay_cap} setVal={v=>updateNguoiKhai('ngay_cap', v)}/></View>
                  <View style={{flex:1}}><InputField label="Nơi cấp" val={nguoiKhai.noi_cap} setVal={v=>updateNguoiKhai('noi_cap', v)}/></View>
              </View>
              <InputField label="Thường trú" val={nguoiKhai.thuong_tru} setVal={v=>updateNguoiKhai('thuong_tru',v)}/>
              <InputField label="Nơi ở hiện tại" val={nguoiKhai.noi_o_hien_tai} setVal={v=>updateNguoiKhai('noi_o_hien_tai',v)}/>
              <TouchableOpacity onPress={()=>updateNguoiKhai('noi_o_hien_tai', nguoiKhai.thuong_tru)}><Text style={{textAlign:'right', color:'#B91C1C', fontWeight:'bold', marginBottom:10}}>⬇️ Giống thường trú</Text></TouchableOpacity>
              <InputField label="Quê quán" val={nguoiKhai.que_quan} setVal={v=>updateNguoiKhai('que_quan',v)}/>
              <View style={styles.row}>
                  <View style={{flex:1, marginRight:5}}><InputField label="Dân tộc" val={nguoiKhai.dan_toc} setVal={v=>updateNguoiKhai('dan_toc',v)}/></View>
                  <View style={{flex:1}}><InputField label="Tôn giáo" val={nguoiKhai.ton_giao} setVal={v=>updateNguoiKhai('ton_giao',v)}/></View>
              </View>
              <InputField label="Trình độ văn hóa" val={nguoiKhai.trinh_do} setVal={v=>updateNguoiKhai('trinh_do',v)}/>
              <InputField label="SĐT (*)" val={nguoiKhai.sdt} setVal={v=>updateNguoiKhai('sdt',v)} keyboard="phone-pad"/>
              <RadioGroup label="Công việc" options={['Thất nghiệp','Đang có việc làm','Hết tuổi lao động','Học sinh']} selected={nguoiKhai.cong_viec} onSelect={v=>updateNguoiKhai('cong_viec',v)}/>
              <TouchableOpacity style={styles.nextBtn} onPress={()=>setActiveTab(2)}><Text style={styles.nextText}>TIẾP TỤC 👉</Text></TouchableOpacity>
            </View>
          )}

          {activeTab === 2 && (
            <View>
              {thanhVien.map((tv, i)=>(
                <View key={i} style={styles.memberCard}>
                  <View style={{flexDirection:'row', justifyContent:'space-between'}}><Text style={styles.memberTitle}>Thành viên {i+1}</Text><TouchableOpacity onPress={()=>xoaThanhVien(i)}><Text style={{color:'red'}}>Xóa</Text></TouchableOpacity></View>
                  
                  <InputField label="Họ tên" val={tv.ho_ten} setVal={v=>updateThanhVien(i,'ho_ten',v.toUpperCase())}/>
                  <InputField label="Quan hệ với chủ hộ" val={tv.quan_he} setVal={v=>updateThanhVien(i,'quan_he',v)}/>
                  
                  <View style={styles.row}>
                      <View style={{flex:1, marginRight:5}}><InputField label="Ngày sinh" val={tv.ngay_sinh} setVal={v=>updateThanhVien(i,'ngay_sinh',v)}/></View>
                      <View style={{flex:1}}><InputField label="CMND/ĐDCN" val={tv.so_cmnd} setVal={v=>updateThanhVien(i,'so_cmnd',v)} keyboard="numeric"/></View>
                  </View>
                  <View style={styles.row}>
                      <View style={{flex:1, marginRight:5}}><InputField label="Ngày cấp" val={tv.ngay_cap} setVal={v=>updateThanhVien(i,'ngay_cap', v)}/></View>
                      <View style={{flex:1}}><InputField label="Nơi cấp" val={tv.noi_cap} setVal={v=>updateThanhVien(i,'noi_cap', v)}/></View>
                  </View>
                  <TouchableOpacity style={styles.copyBtn} onPress={()=>copyDiaChi(i)}><Text style={{color:'#fff'}}>📋 Chép địa chỉ chủ hộ</Text></TouchableOpacity>
                  <InputField label="Thường trú" val={tv.thuong_tru} setVal={v=>updateThanhVien(i,'thuong_tru',v)}/>
                  <InputField label="Hiện tại" val={tv.noi_o_hien_tai} setVal={v=>updateThanhVien(i,'noi_o_hien_tai',v)}/>
                  <View style={styles.row}>
                      <View style={{flex:1, marginRight:5}}><InputField label="Dân tộc" val={tv.dan_toc} setVal={v=>updateThanhVien(i,'dan_toc',v)}/></View>
                      <View style={{flex:1}}><InputField label="Tôn giáo" val={tv.ton_giao} setVal={v=>updateThanhVien(i,'ton_giao',v)}/></View>
                  </View>
                  <InputField label="Trình độ văn hóa" val={tv.trinh_do} setVal={v=>updateThanhVien(i,'trinh_do',v)}/>
                  <InputField label="Chuyên môn" val={tv.chuyen_mon} setVal={v=>updateThanhVien(i,'chuyen_mon',v)}/>
                  <InputField label="Quốc tịch" val={tv.quoc_tich} setVal={v=>updateThanhVien(i,'quoc_tich',v)}/>
                  <Text style={styles.label}>Tình trạng (Chọn nhiều):</Text>
                  <View style={{flexDirection:'row', flexWrap:'wrap'}}>
                    {['Thất nghiệp','Đang có việc làm','Hết tuổi lao động','Học sinh','Trẻ sơ sinh','Sống Một Mình'].map(tt=>(
                      <TouchableOpacity key={tt} style={[styles.checkbox, tv.tinh_trang.includes(tt)&&styles.checkboxSelected]}
                        onPress={()=>{ const c=tv.tinh_trang; updateThanhVien(i,'tinh_trang', c.includes(tt)?c.filter(x=>x!==tt):[...c,tt]); }}>
                        <Text style={tv.tinh_trang.includes(tt)?styles.textSelected:{color:'#333'}}>{tt}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              ))}
              <TouchableOpacity style={styles.addBtn} onPress={themThanhVien}><Text style={styles.addText}>+ THÊM THÀNH VIÊN</Text></TouchableOpacity>
              <TouchableOpacity style={styles.submitBtn} onPress={guiHoSo} disabled={loading}><Text style={styles.submitText}>{loading?"ĐANG GỬI...":"LƯU HỒ SƠ"}</Text></TouchableOpacity>
            </View>
          )}
          <View style={{height:50}}/>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  header: { backgroundColor: '#B91C1C', padding: 15, paddingTop: 40, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerTitle: { fontSize: 16, fontWeight: 'bold', color: '#fff' },
  authContainer: { flex: 1, backgroundColor: '#8B1818', justifyContent: 'center', padding: 20 },
  logoBox: { alignItems: 'center', marginBottom: 40 },
  logoText: { fontSize: 40, fontWeight: 'bold', color: '#FFD700', letterSpacing: 2 },
  logoSub: { color: '#fff', fontSize: 14, fontWeight: 'bold', textAlign:'center' },
  authBox: { backgroundColor: '#fff', padding: 20, borderRadius: 10 },
  authTitle: { fontSize: 22, fontWeight: 'bold', color: '#8B1818', textAlign: 'center', marginBottom: 20 },
  authInput: { backgroundColor: '#F3F4F6', padding: 15, borderRadius: 8, marginBottom: 15 },
  authBtn: { backgroundColor: '#B91C1C', padding: 15, borderRadius: 8, alignItems: 'center' },
  authBtnText: { color: '#fff', fontWeight: 'bold' },
  tabContainer: { flexDirection: 'row', backgroundColor: '#fff' },
  tabBtn: { flex: 1, padding: 15, alignItems: 'center', borderBottomWidth: 3, borderBottomColor: 'transparent' },
  tabActive: { borderBottomColor: '#B91C1C' },
  tabText: { fontWeight: 'bold', color: '#6B7280' },
  textSelected: { color: '#B91C1C' },
  body: { padding: 15 },
  inputGroup: { marginBottom: 15 },
  label: { fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 5 },
  input: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 6, padding: 10 },
  row: { flexDirection: 'row' },
  radioBtn: { flexDirection: 'row', alignItems: 'center', padding: 8, borderWidth: 1, borderColor: '#ccc', borderRadius: 20, marginRight: 8, marginBottom: 8 },
  radioSelected: { borderColor: '#B91C1C', backgroundColor: '#FEF2F2' },
  radioCircle: { width: 16, height: 16, borderRadius: 8, borderWidth: 1, borderColor: '#ccc', marginRight: 5 },
  radioCircleSelected: { backgroundColor: '#B91C1C', borderColor: '#B91C1C' },
  radioText: { fontSize: 13 },
  nextBtn: { backgroundColor: '#4B5563', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 20 },
  nextText: { color: '#fff', fontWeight: 'bold' },
  memberCard: { backgroundColor: '#fff', padding: 10, borderRadius: 8, marginBottom: 15, borderLeftWidth: 4, borderLeftColor: '#B91C1C' },
  memberTitle: { fontWeight: 'bold', color: '#B91C1C', marginBottom: 10 },
  copyBtn: { backgroundColor: '#059669', padding: 8, borderRadius: 5, alignItems: 'center', marginVertical: 10 },
  addBtn: { borderWidth: 1, borderColor: '#B91C1C', padding: 15, borderRadius: 8, alignItems: 'center', borderStyle: 'dashed', marginBottom: 10 },
  addText: { color: '#B91C1C', fontWeight: 'bold' },
  submitBtn: { backgroundColor: '#B91C1C', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  submitText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  checkbox: { padding: 8, borderWidth: 1, borderColor: '#ccc', borderRadius: 4, marginRight: 8, marginBottom: 8 },
  checkboxSelected: { backgroundColor: '#FEF2F2', borderColor: '#B91C1C' },
  textSelected: { color: '#B91C1C' }
});

export default function App() {
  const [screen, setScreen] = useState('LOGIN'); 
  const [currentUser, setCurrentUser] = useState(null);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setScreen('HOME');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setScreen('LOGIN');
  };

  if (screen === 'LOGIN') return <LoginScreen onLoginSuccess={handleLoginSuccess} onGoRegister={() => setScreen('REGISTER')} />;
  if (screen === 'REGISTER') return <RegisterScreen onGoLogin={() => setScreen('LOGIN')} />;
  return <MainForm user={currentUser} onLogout={handleLogout} />;
}