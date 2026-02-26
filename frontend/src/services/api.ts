import axios from 'axios';
import { Platform } from 'react-native';
import { OCRResult } from '../types/navigation';

// Tailscale IP for remote access via Expo Go
// Use this when phone is on different network than PC
const getBaseURL = () => {
  return 'http://100.69.255.57:8000';
};

export const API_BASE_URL = getBaseURL();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadReceipt = async (imageUri: string): Promise<OCRResult> => {
  const formData = new FormData();
  
  const filename = imageUri.split('/').pop() || 'receipt.jpg';
  const match = /\.(\w+)$/.exec(filename);
  const type = match ? `image/${match[1]}` : 'image/jpeg';

  formData.append('file', {
    uri: imageUri,
    name: filename,
    type: type,
  } as any);

  const response = await apiClient.post<OCRResult>('/api/ocr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export default apiClient;
