export interface OrderItem {
  name: string;
  quantity: number;
  price: number;
}

export interface OCRResult {
  order_number: string;
  restaurant: string;
  items: OrderItem[];
  subtotal: number;
  total: number;
  is_valid: boolean;
  errors: string[];
}

export type RootStackParamList = {
  Dashboard: undefined;
  Loading: {
    imageUri: string;
  };
  FormCorrection: {
    ocrResult: OCRResult;
  };
};
