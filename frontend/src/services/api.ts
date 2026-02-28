import axios from 'axios';
import { Platform } from 'react-native';
import { OCRResult } from '../types/navigation';

// Base URL configuration
// - Android emulator: 10.0.2.2 maps to host machine's localhost
// - Physical device: use your machine's LAN IP
// - iOS simulator / web: localhost works fine
//
// To find your LAN IP, check the Expo dev server output (e.g., exp://192.168.x.x:8081)
// or run `ipconfig` (Windows) / `ifconfig` (macOS/Linux).
const DEV_MACHINE_IP = '192.168.3.201';

const getBaseURL = () => {
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }
  // iOS (physical device or simulator) — use LAN IP
  return `http://${DEV_MACHINE_IP}:8000`;
};


export const API_BASE_URL = getBaseURL();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadReceipt = async (imageUris: string[]): Promise<OCRResult> => {
  const formData = new FormData();
  
  imageUris.forEach((uri, index) => {
    const filename = uri.split('/').pop() || `receipt_${index}.jpg`;
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';

    formData.append('files', {
      uri: uri,
      name: filename,
      type: type,
    } as any);
  });

  const response = await apiClient.post<OCRResult>('/api/ocr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export default apiClient;
