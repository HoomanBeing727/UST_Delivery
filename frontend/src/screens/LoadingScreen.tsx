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
import { RootStackParamList } from '../types/navigation';
import { uploadReceipt } from '../services/api';

type Props = NativeStackScreenProps<RootStackParamList, 'Loading'>;

const MESSAGES = [
  'Uploading image…',
  'Running OCR…',
  'Extracting order details…',
  'Almost there…',
];

export default function LoadingScreen({ navigation, route }: Props) {
  const { colors } = useTheme();
  const { imageUri } = route.params;
  const [messageIdx, setMessageIdx] = useState(0);
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const hasNavigated = useRef(false);

  // Cycle through loading messages
  useEffect(() => {
    const interval = setInterval(() => {
      Animated.sequence([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();

      setMessageIdx((prev) => (prev + 1) % MESSAGES.length);
    }, 2500);

    return () => clearInterval(interval);
  }, [fadeAnim]);

  // Upload + OCR call
  useEffect(() => {
    let cancelled = false;

    const process = async () => {
      try {
        const result = await uploadReceipt(imageUri);

        if (cancelled || hasNavigated.current) return;
        hasNavigated.current = true;

        navigation.replace('FormCorrection', { ocrResult: result });
      } catch (error: unknown) {
        if (cancelled || hasNavigated.current) return;
        hasNavigated.current = true;

        let message = 'Something went wrong while processing your receipt.';
        if (error instanceof Error) {
          // Axios wraps the response in error.message or error.response.data
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
  }, [imageUri, navigation]);

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.content}>
        <View style={[styles.loaderBox, { backgroundColor: colors.surface }]}>
          <ActivityIndicator
            size="large"
            color={colors.accent}
            style={styles.spinner}
          />
          <Animated.Text
            style={[
              styles.message,
              { color: colors.text, opacity: fadeAnim },
            ]}
          >
            {MESSAGES[messageIdx]}
          </Animated.Text>
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
