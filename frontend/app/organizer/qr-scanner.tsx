import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
} from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import { useApi } from '../../../context/AuthContext';
import { colors, spacing, borderRadius, typography } from '../../theme';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';

export default function QRScanner() {
  const api = useApi();
  const router = useRouter();
  const params = useLocalSearchParams();
  const eventId = params.eventId as string;
  
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [studentName, setStudentName] = useState('');

  useEffect(() => {
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleBarCodeScanned = async ({ type, data }: any) => {
    setScanned(true);
    
    try {
      const response = await api.post('/attendance/mark', {
        qr_code_data: data,
      });
      
      setStudentName(response.data.student_name);
      setShowSuccess(true);
      
      // Auto-close success modal after 2 seconds
      setTimeout(() => {
        setShowSuccess(false);
        setScanned(false);
      }, 2000);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Invalid QR code');
      setScanned(false);
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Ionicons name="camera-off" size={64} color={colors.textSecondary} />
        <Text style={styles.text}>No access to camera</Text>
        <Text style={styles.subtext}>Please enable camera permissions in settings</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.white} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Scan QR Code</Text>
      </View>

      <BarCodeScanner
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={StyleSheet.absoluteFillObject}
      />

      <View style={styles.overlay}>
        <View style={styles.scanArea}>
          <View style={[styles.corner, styles.topLeft]} />
          <View style={[styles.corner, styles.topRight]} />
          <View style={[styles.corner, styles.bottomLeft]} />
          <View style={[styles.corner, styles.bottomRight]} />
        </View>
        
        <View style={styles.instructionContainer}>
          <Text style={styles.instruction}>Position QR code within the frame</Text>
        </View>
      </View>

      {/* Success Modal */}
      <Modal
        visible={showSuccess}
        animationType="fade"
        transparent={true}
      >
        <View style={styles.successModalOverlay}>
          <View style={styles.successModal}>
            <Ionicons name="checkmark-circle" size={64} color={colors.success} />
            <Text style={styles.successTitle}>Attendance Marked!</Text>
            <Text style={styles.successName}>{studentName}</Text>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.black,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    paddingTop: 60,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    zIndex: 10,
  },
  backButton: {
    padding: spacing.sm,
  },
  headerTitle: {
    ...typography.h3,
    color: colors.white,
    marginLeft: spacing.md,
  },
  text: {
    ...typography.h3,
    color: colors.white,
    textAlign: 'center',
    marginTop: spacing.md,
  },
  subtext: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: 250,
    height: 250,
    position: 'relative',
  },
  corner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: colors.primary,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderTopWidth: 4,
    borderLeftWidth: 4,
  },
  topRight: {
    top: 0,
    right: 0,
    borderTopWidth: 4,
    borderRightWidth: 4,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderBottomWidth: 4,
    borderRightWidth: 4,
  },
  instructionContainer: {
    position: 'absolute',
    bottom: 100,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: spacing.md,
    borderRadius: borderRadius.md,
  },
  instruction: {
    ...typography.body,
    color: colors.white,
    textAlign: 'center',
  },
  successModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  successModal: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    alignItems: 'center',
    minWidth: 250,
  },
  successTitle: {
    ...typography.h2,
    color: colors.text,
    marginTop: spacing.md,
  },
  successName: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
});