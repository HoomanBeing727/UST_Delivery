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


export default function LoadingScreen({ navigation, route }: Props) {
  const { colors } = useTheme();
  // Extract imageUris from route params
  const { imageUris } = route.params;
  
  const [totalImages] = useState(imageUris.length || 1);
  const hasNavigated = useRef(false);


  useEffect(() => {
    let cancelled = false;

    const process = async () => {
      try {
        if (imageUris.length === 0) {
           throw new Error('No images provided');
        }

        const finalResult = await uploadReceipt(imageUris);
        
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
              ? `Processing ${totalImages} images...`
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
