import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../context/ThemeContext';
import { RootStackParamList, OrderItem } from '../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'FormCorrection'>;

export default function FormCorrectionScreen({ navigation, route }: Props) {
  const { colors } = useTheme();
  const { ocrResult } = route.params;

  const [orderNumber, setOrderNumber] = useState(ocrResult.order_number);
  const [restaurant, setRestaurant] = useState(ocrResult.restaurant);
  const [items, setItems] = useState<OrderItem[]>(
    ocrResult.items.length > 0
      ? ocrResult.items
      : [{ name: '', quantity: 1, price: 0 }],
  );
  const [subtotal, setSubtotal] = useState(String(ocrResult.subtotal));
  const [total, setTotal] = useState(String(ocrResult.total));

  const isValid = ocrResult.is_valid;

  const updateItem = (index: number, field: keyof OrderItem, value: string) => {
    setItems((prev) => {
      const updated = [...prev];
      if (field === 'name') {
        updated[index] = { ...updated[index], name: value };
      } else if (field === 'quantity') {
        const num = parseInt(value, 10);
        updated[index] = { ...updated[index], quantity: isNaN(num) ? 0 : num };
      } else if (field === 'price') {
        const num = parseFloat(value);
        updated[index] = { ...updated[index], price: isNaN(num) ? 0 : num };
      }
      return updated;
    });
  };

  const addItem = () => {
    setItems((prev) => [...prev, { name: '', quantity: 1, price: 0 }]);
  };

  const removeItem = (index: number) => {
    if (items.length <= 1) {
      Alert.alert('Cannot Remove', 'You must have at least one item.');
      return;
    }
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleConfirm = () => {
    // Validate required fields
    if (!orderNumber.trim()) {
      Alert.alert('Missing Info', 'Please enter an order number.');
      return;
    }
    if (!restaurant.trim()) {
      Alert.alert('Missing Info', 'Please enter the restaurant name.');
      return;
    }
    if (items.some((item) => !item.name.trim())) {
      Alert.alert('Missing Info', 'All items must have a name.');
      return;
    }

    const finalOrder = {
      order_number: orderNumber.trim(),
      restaurant: restaurant.trim(),
      items: items.map((item) => ({
        name: item.name.trim(),
        quantity: item.quantity || 1,
        price: item.price || 0,
      })),
      subtotal: parseFloat(subtotal) || 0,
      total: parseFloat(total) || 0,
    };

    Alert.alert(
      'Order Confirmed',
      `Order #${finalOrder.order_number}\n${finalOrder.items.length} item(s)\nTotal: HK$ ${finalOrder.total.toFixed(2)}`,
      [
        {
          text: 'Back to Dashboard',
          onPress: () => navigation.navigate('Dashboard'),
        },
      ],
    );
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: colors.background }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content}>
        {/* HKUST Validation Banner */}
        {!isValid && (
          <View style={[styles.banner, { backgroundColor: colors.error }]}>
            <Text style={styles.bannerText}>
              ⚠️ This order is NOT from HKUST McDonald's. It cannot be delivered through this platform.
            </Text>
          </View>
        )}

        {isValid && (
          <View style={[styles.banner, { backgroundColor: colors.success }]}>
            <Text style={styles.bannerText}>
              ✅ HKUST McDonald's order verified
            </Text>
          </View>
        )}

        {/* OCR Errors */}
        {ocrResult.errors.length > 0 && (
          <View style={[styles.errorsBox, { borderColor: colors.error }]}>
            <Text style={[styles.errorsTitle, { color: colors.error }]}>
              OCR Issues:
            </Text>
            {ocrResult.errors.map((err, i) => (
              <Text key={i} style={[styles.errorItem, { color: colors.error }]}>
                • {err}
              </Text>
            ))}
          </View>
        )}

        {/* Order Number */}
        <Text style={[styles.label, { color: colors.text }]}>Order Number</Text>
        <TextInput
          style={[
            styles.input,
            {
              backgroundColor: colors.surface,
              color: colors.text,
              borderColor: colors.border,
            },
          ]}
          value={orderNumber}
          onChangeText={setOrderNumber}
          placeholder="e.g. 163"
          placeholderTextColor={colors.textSecondary}
          keyboardType="number-pad"
        />

        {/* Restaurant */}
        <Text style={[styles.label, { color: colors.text }]}>Restaurant</Text>
        <TextInput
          style={[
            styles.input,
            {
              backgroundColor: colors.surface,
              color: colors.text,
              borderColor: colors.border,
            },
          ]}
          value={restaurant}
          onChangeText={setRestaurant}
          placeholder="e.g. The Hong Kong University of Science & Technology"
          placeholderTextColor={colors.textSecondary}
        />

        {/* Items */}
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Items ({items.length})
          </Text>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: colors.accent }]}
            onPress={addItem}
          >
            <Text style={styles.addButtonText}>+ Add Item</Text>
          </TouchableOpacity>
        </View>

        {items.map((item, index) => (
          <View
            key={index}
            style={[styles.itemCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={styles.itemHeader}>
              <Text style={[styles.itemLabel, { color: colors.textSecondary }]}>
                Item {index + 1}
              </Text>
              <TouchableOpacity onPress={() => removeItem(index)}>
                <Text style={[styles.removeText, { color: colors.error }]}>
                  Remove
                </Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.background,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              value={item.name}
              onChangeText={(v) => updateItem(index, 'name', v)}
              placeholder="Item name"
              placeholderTextColor={colors.textSecondary}
            />

            <View style={styles.itemRow}>
              <View style={styles.itemFieldHalf}>
                <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>
                  Qty
                </Text>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.background,
                      color: colors.text,
                      borderColor: colors.border,
                    },
                  ]}
                  value={String(item.quantity)}
                  onChangeText={(v) => updateItem(index, 'quantity', v)}
                  keyboardType="number-pad"
                  placeholder="1"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>

              <View style={styles.itemFieldHalf}>
                <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>
                  Price (HK$)
                </Text>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.background,
                      color: colors.text,
                      borderColor: colors.border,
                    },
                  ]}
                  value={String(item.price)}
                  onChangeText={(v) => updateItem(index, 'price', v)}
                  keyboardType="decimal-pad"
                  placeholder="0.00"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
            </View>
          </View>
        ))}

        {/* Subtotal & Total */}
        <View style={styles.totalsRow}>
          <View style={styles.totalField}>
            <Text style={[styles.label, { color: colors.text }]}>Subtotal (HK$)</Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.surface,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              value={subtotal}
              onChangeText={setSubtotal}
              keyboardType="decimal-pad"
              placeholder="0.00"
              placeholderTextColor={colors.textSecondary}
            />
          </View>

          <View style={styles.totalField}>
            <Text style={[styles.label, { color: colors.text }]}>Total (HK$)</Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.surface,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              value={total}
              onChangeText={setTotal}
              keyboardType="decimal-pad"
              placeholder="0.00"
              placeholderTextColor={colors.textSecondary}
            />
          </View>
        </View>

        {/* Confirm Button */}
        <TouchableOpacity
          style={[
            styles.confirmButton,
            { backgroundColor: isValid ? colors.accent : '#999' },
          ]}
          onPress={handleConfirm}
          disabled={!isValid}
          activeOpacity={0.8}
        >
          <Text style={styles.confirmButtonText}>
            {isValid ? '✓ Confirm Order' : '✗ Cannot Submit (Not HKUST)'}
          </Text>
        </TouchableOpacity>

        {/* Start Over */}
        <TouchableOpacity
          style={styles.startOverButton}
          onPress={() => navigation.navigate('Dashboard')}
          activeOpacity={0.7}
        >
          <Text style={[styles.startOverText, { color: colors.accent }]}>
            ← Upload a different receipt
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  banner: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  bannerText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
  },
  errorsBox: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
  },
  errorsTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 6,
  },
  errorItem: {
    fontSize: 14,
    marginLeft: 8,
    marginTop: 2,
  },
  label: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 6,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    marginBottom: 4,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '800',
  },
  addButton: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 14,
  },
  itemCard: {
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  itemLabel: {
    fontSize: 14,
    fontWeight: '600',
  },
  removeText: {
    fontSize: 14,
    fontWeight: '700',
  },
  itemRow: {
    flexDirection: 'row',
    gap: 12,
  },
  itemFieldHalf: {
    flex: 1,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 4,
    marginTop: 6,
  },
  totalsRow: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 8,
  },
  totalField: {
    flex: 1,
  },
  confirmButton: {
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    marginTop: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 5,
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '800',
  },
  startOverButton: {
    alignItems: 'center',
    marginTop: 20,
    padding: 12,
  },
  startOverText: {
    fontSize: 16,
    fontWeight: '700',
  },
});
