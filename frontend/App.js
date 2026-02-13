import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, TextInput, TouchableOpacity, Alert, ActivityIndicator, Keyboard } from 'react-native';

// --- QUAN TRỌNG: THAY IP CỦA BẠN VÀO ĐÂY ---
// Giữ nguyên đuôi :8000/api...
const IP_MAY_TINH = '192.168.0.100'; 
const API_URL = `http://${IP_MAY_TINH}:8000/api`;

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  // Biến lưu thông tin nhập vào
  const [ten, setTen] = useState('');
  const [canHo, setCanHo] = useState('');
  const [sdt, setSdt] = useState('');

  // 1. Hàm tải danh sách từ Server
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/cu-dan`);
      const json = await response.json();
      setData(json);
    } catch (error) {
      Alert.alert("Lỗi", "Không kết nối được với máy tính! Kiểm tra IP.");
    } finally {
      setLoading(false);
    }
  };

  // 2. Hàm gửi dữ liệu mới lên Server
  const handleThemMoi = async () => {
    if (!ten || !canHo || !sdt) {
      Alert.alert("Thiếu thông tin", "Vui lòng nhập đủ Tên, Căn hộ và SĐT");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/them-cu-dan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ten: ten,
          can_ho: canHo,
          sdt: sdt,
        }),
      });

      if (response.ok) {
        Alert.alert("Thành công", "Đã thêm cư dân mới!");
        setTen(''); setCanHo(''); setSdt(''); // Xóa trắng ô nhập
        Keyboard.dismiss(); // Ẩn bàn phím
        fetchData(); // Tải lại danh sách mới
      } else {
        Alert.alert("Lỗi", "Server trả về lỗi.");
      }
    } catch (error) {
      Alert.alert("Lỗi", "Không gửi được dữ liệu.");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.header}>QUẢN LÝ DÂN CƯ</Text>

      {/* --- FORM NHẬP LIỆU --- */}
      <View style={styles.formContainer}>
        <TextInput 
          style={styles.input} 
          placeholder="Họ và Tên" 
          value={ten} onChangeText={setTen} 
        />
        <TextInput 
          style={styles.input} 
          placeholder="Số Căn Hộ (VD: A101)" 
          value={canHo} onChangeText={setCanHo} 
        />
        <TextInput 
          style={styles.input} 
          placeholder="Số Điện Thoại" 
          keyboardType="numeric"
          value={sdt} onChangeText={setSdt} 
        />
        
        <TouchableOpacity style={styles.button} onPress={handleThemMoi}>
          <Text style={styles.buttonText}>THÊM CƯ DÂN</Text>
        </TouchableOpacity>
      </View>

      {/* --- DANH SÁCH HIỂN THỊ --- */}
      <Text style={styles.subHeader}>Danh sách hiện tại:</Text>
      {loading ? <ActivityIndicator color="blue" /> : (
        <FlatList
          data={data}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View>
                <Text style={styles.name}>{item.ten}</Text>
                <Text style={styles.info}>🏠 {item.can_ho} - 📞 {item.sdt}</Text>
              </View>
            </View>
          )}
        />
      )}
    </View>
  );
}

// --- TRANG TRÍ GIAO DIỆN (CSS) ---
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f2f5', paddingTop: 50, paddingHorizontal: 20 },
  header: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginBottom: 20, color: '#1a73e8' },
  subHeader: { fontSize: 18, fontWeight: 'bold', marginTop: 20, marginBottom: 10, color: '#333' },
  
  formContainer: { backgroundColor: 'white', padding: 15, borderRadius: 10, elevation: 3 },
  input: { borderWidth: 1, borderColor: '#ddd', padding: 10, marginBottom: 10, borderRadius: 5, fontSize: 16 },
  
  button: { backgroundColor: '#1a73e8', padding: 15, borderRadius: 5, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },

  card: { backgroundColor: 'white', padding: 15, marginBottom: 10, borderRadius: 8, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 1 },
  name: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  info: { color: '#666', marginTop: 5 },
});