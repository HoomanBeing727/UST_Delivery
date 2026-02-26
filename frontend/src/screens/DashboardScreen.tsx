import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import { useTheme } from '../context/ThemeContext';
import { RootStackParamList } from '../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'Dashboard'>;

export default function DashboardScreen({ navigation }: Props) {
  const { isDark, toggleTheme, colors } = useTheme();

  const requestPermissions = async () => {
    if (Platform.OS !== 'web') {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Sorry, we need camera roll permissions to upload receipts!',
          [{ text: 'OK' }]
        );
        return false;
      }
    }
    return true;
  };

  const handleUploadReceipt = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      navigation.navigate('Loading', {
        imageUri: result.assets[0].uri,
      });
    }
  };

  const handlePlaceholder = (feature: string) => {
    Alert.alert('Coming Soon', `${feature} will be available in the next update!`, [
      { text: 'OK' },
    ]);
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.contentContainer}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>DeliverU</Text>
        <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
          Student-to-Student Delivery
        </Text>
      </View>

      {/* Dark Mode Toggle */}
      <View style={[styles.card, { backgroundColor: colors.surface }]}>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={[styles.settingTitle, { color: colors.text }]}>
              {isDark ? '🌙' : '☀️'} Dark Mode
            </Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              {isDark ? 'Switch to light theme' : 'Switch to dark theme'}
            </Text>
          </View>
          <Switch
            value={isDark}
            onValueChange={toggleTheme}
            trackColor={{ false: '#D1D5DB', true: colors.accent }}
            thumbColor={isDark ? colors.primary : '#F3F4F6'}
            ios_backgroundColor="#D1D5DB"
          />
        </View>
      </View>

      {/* Upload Receipt Button */}
      <TouchableOpacity
        style={styles.uploadButton}
        onPress={handleUploadReceipt}
        activeOpacity={0.8}
      >
        <View style={styles.uploadButtonContent}>
          <Text style={styles.uploadButtonIcon}>📸</Text>
          <View>
            <Text style={styles.uploadButtonText}>Upload Receipt</Text>
            <Text style={styles.uploadButtonSubtext}>Tap to select from gallery</Text>
          </View>
        </View>
      </TouchableOpacity>

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: colors.surface }]}
          onPress={() => handlePlaceholder('Manage Profile')}
          activeOpacity={0.7}
        >
          <Text style={styles.actionIcon}>👤</Text>
          <Text style={[styles.actionText, { color: colors.text }]}>Manage Profile</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: colors.surface }]}
          onPress={() => handlePlaceholder('FAQ / Help')}
          activeOpacity={0.7}
        >
          <Text style={styles.actionIcon}>❓</Text>
          <Text style={[styles.actionText, { color: colors.text }]}>FAQ / Help</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: colors.surface }]}
          onPress={() => handlePlaceholder('Logout')}
          activeOpacity={0.7}
        >
          <Text style={styles.actionIcon}>🚪</Text>
          <Text style={[styles.actionText, { color: colors.text }]}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={[styles.footerText, { color: colors.textSecondary }]}>
          Made with ❤️ for HKUST Students
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 24,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
  },
  header: {
    marginBottom: 32,
    alignItems: 'center',
  },
  title: {
    fontSize: 36,
    fontWeight: '800',
    letterSpacing: -1,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    fontWeight: '500',
  },
  card: {
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    fontWeight: '500',
  },
  uploadButton: {
    backgroundColor: '#0055de',
    borderRadius: 20,
    padding: 24,
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 5,
  },
  uploadButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadButtonIcon: {
    fontSize: 48,
    marginRight: 16,
  },
  uploadButtonText: {
    fontSize: 22,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  uploadButtonSubtext: {
    fontSize: 14,
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.85)',
    marginTop: 4,
  },
  actionsContainer: {
    gap: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  actionIcon: {
    fontSize: 28,
    marginRight: 16,
  },
  actionText: {
    fontSize: 17,
    fontWeight: '700',
  },
  footer: {
    marginTop: 48,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    fontWeight: '600',
  },
});
