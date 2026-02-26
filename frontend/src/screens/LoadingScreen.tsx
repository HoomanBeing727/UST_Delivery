import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Animated,
  Alert,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../context/ThemeContext';
import { RootStackParamList, OCRResult, OrderItem } from '../types/navigation';
import { uploadReceipt } from '../services/api';

type Props = NativeStackScreenProps<RootStackParamList, 'Loading'>;

// Progress messages are now dynamic based on image count
// Helper function to merge multiple OCR results
const mergeOCRResults = (results: OCRResult[]): OCRResult => {
  if (results.length === 0) {
    throw new Error('No OCR results to merge');
  }

  const allItems: OrderItem[] = [];
  let totalSubtotal = 0;
  let totalAmount = 0;
  const allErrors: string[] = [];
  let anyValid = false;
  
  // Use the first result's metadata as base, but merge items/totals
  const baseResult = results[0];

  for (const result of results) {
    allItems.push(...result.items);
    totalSubtotal += result.subtotal;
    totalAmount += result.total;
    allErrors.push(...result.errors);
    if (result.is_valid) anyValid = true;
  }
  
  return {
    order_number: baseResult.order_number, 
    items: allItems,
    subtotal: totalSubtotal,
    total: totalAmount,
    is_valid: anyValid,
    errors: allErrors,
  };
};


export default function LoadingScreen({ navigation, route }: Props) {
  const { colors } = useTheme();
  // Extract imageUris from route params
  const { imageUris } = route.params;
  
  const [currentImage, setCurrentImage] = useState(1);
  const [totalImages] = useState(imageUris.length || 1);
  const hasNavigated = useRef(false);


  useEffect(() => {
    let cancelled = false;

    const process = async () => {
      try {
        if (imageUris.length === 0) {
           throw new Error('No images provided');
        }

        const results: OCRResult[] = [];
        
        for (let i = 0; i < imageUris.length; i++) {
          if (cancelled || hasNavigated.current) return;
          
          setCurrentImage(i + 1);
          const result = await uploadReceipt(imageUris[i]);
          results.push(result);
        }

        if (cancelled || hasNavigated.current) return;
        
        // Merge results if we have multiple, otherwise just take the first
        const finalResult = results.length > 1 ? mergeOCRResults(results) : results[0];
        
        hasNavigated.current = true;
        navigation.replace('FormCorrection', { ocrResult: finalResult });
      } catch (error: unknown) {
        if (cancelled || hasNavigated.current) return;
        hasNavigated.current = true;

        let message = 'Something went wrong while processing your receipt.';
        if (error instanceof Error) {
          message = error.message;
        }

        Alert.alert('OCR Failed', message, [
          {
            text: 'Go Back',
            onPress: () => navigation.goBack(),
          },
        ]);
      }
    };

    process();

    return () => {
      cancelled = true;
    };
  }, [imageUris, navigation]);

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.content}>
        <View style={[styles.loaderBox, { backgroundColor: colors.surface }]}>
          <ActivityIndicator
            size="large"
            color="#0055de"
            style={styles.spinner}
          />
          <Text style={[styles.message, { color: colors.text }]}>
            {totalImages > 1 
              ? `Processing image ${currentImage} of ${totalImages}...`
              : 'Processing receipt...'}
          </Text>
          <Text style={[styles.hint, { color: colors.textSecondary }]}>
            This may take a few seconds
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loaderBox: {
    borderRadius: 24,
    padding: 40,
    alignItems: 'center',
    width: '100%',
    maxWidth: 320,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
  },
  spinner: {
    marginBottom: 24,
    transform: [{ scale: 1.5 }],
  },
  message: {
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 12,
  },
  hint: {
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
});
