import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { useApi } from '../../../context/AuthContext';
import { colors, spacing, borderRadius, typography } from '../../theme';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { format } from 'date-fns';
import QRCode from 'react-native-qrcode-svg';

interface Registration {
  id: string;
  event_title: string;
  event_id: string;
  qr_code_data: string;
  attendance_marked: boolean;
  attendance_time: string | null;
  certificate_issued: boolean;
  created_at: string;
}

export default function MyEvents() {
  const api = useApi();
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedReg, setSelectedReg] = useState<Registration | null>(null);
  const [showQRModal, setShowQRModal] = useState(false);
  const [tab, setTab] = useState<'all' | 'upcoming' | 'attended'>('all');

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      const response = await api.get('/registrations/my-registrations');
      setRegistrations(response.data);
    } catch (error) {
      console.error('Error fetching registrations:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchRegistrations();
  };

  const handleShowQR = (reg: Registration) => {
    setSelectedReg(reg);
    setShowQRModal(true);
  };

  const filteredRegistrations = registrations.filter(reg => {
    if (tab === 'attended') return reg.attendance_marked;
    if (tab === 'upcoming') return !reg.attendance_marked;
    return true;
  });

  const renderRegistration = ({ item }: { item: Registration }) => {
    return (
      <View style={styles.eventCard}>
        <View style={styles.eventHeader}>
          <Text style={styles.eventTitle}>{item.event_title}</Text>
          {item.certificate_issued && (
            <Ionicons name="trophy" size={24} color={colors.accent} />
          )}
        </View>
        
        <View style={styles.statusContainer}>
          {item.attendance_marked ? (
            <View style={[styles.statusBadge, { backgroundColor: colors.success }]}>
              <Ionicons name="checkmark-circle" size={16} color={colors.white} />
              <Text style={styles.statusText}>Attended</Text>
            </View>
          ) : (
            <View style={[styles.statusBadge, { backgroundColor: colors.warning }]}>
              <Ionicons name="time" size={16} color={colors.white} />
              <Text style={styles.statusText}>Pending</Text>
            </View>
          )}
          
          <Text style={styles.registeredDate}>
            Registered: {format(new Date(item.created_at), 'MMM dd, yyyy')}
          </Text>
        </View>
        
        {item.attendance_time && (
          <Text style={styles.attendanceTime}>
            Attended on: {format(new Date(item.attendance_time), 'MMM dd, yyyy HH:mm')}
          </Text>
        )}
        
        <View style={styles.actionsContainer}>
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => handleShowQR(item)}
          >
            <Ionicons name="qr-code" size={20} color={colors.primary} />
            <Text style={styles.actionButtonText}>View QR</Text>
          </TouchableOpacity>
          
          {item.certificate_issued && (
            <TouchableOpacity style={[styles.actionButton, { backgroundColor: colors.accent }]}>
              <Ionicons name="download" size={20} color={colors.white} />
              <Text style={[styles.actionButtonText, { color: colors.white }]}>Certificate</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Events</Text>
        <Text style={styles.headerSubtitle}>{registrations.length} total registrations</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <TouchableOpacity 
          style={[styles.tab, tab === 'all' && styles.activeTab]}
          onPress={() => setTab('all')}
        >
          <Text style={[styles.tabText, tab === 'all' && styles.activeTabText]}>All</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tab, tab === 'upcoming' && styles.activeTab]}
          onPress={() => setTab('upcoming')}
        >
          <Text style={[styles.tabText, tab === 'upcoming' && styles.activeTabText]}>Upcoming</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tab, tab === 'attended' && styles.activeTab]}
          onPress={() => setTab('attended')}
        >
          <Text style={[styles.tabText, tab === 'attended' && styles.activeTabText]}>Attended</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={filteredRegistrations}
          renderItem={renderRegistration}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} colors={[colors.primary]} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="calendar-outline" size={64} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No events yet</Text>
              <Text style={styles.emptySubtext}>Start exploring and register for events!</Text>
            </View>
          }
        />
      )}

      {/* QR Code Modal */}
      <Modal
        visible={showQRModal}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setShowQRModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <TouchableOpacity 
              style={styles.closeButton}
              onPress={() => setShowQRModal(false)}
            >
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
            
            {selectedReg && (
              <View style={styles.qrContainer}>
                <Text style={styles.qrTitle}>{selectedReg.event_title}</Text>
                <Text style={styles.qrSubtitle}>Show this QR code at the event</Text>
                
                <View style={styles.qrCodeContainer}>
                  <QRCode
                    value={selectedReg.qr_code_data}
                    size={220}
                    color={colors.text}
                    backgroundColor={colors.white}
                  />
                </View>
                
                {selectedReg.attendance_marked ? (
                  <View style={[styles.statusBadge, { backgroundColor: colors.success, marginTop: spacing.lg }]}>
                    <Ionicons name="checkmark-circle" size={20} color={colors.white} />
                    <Text style={[styles.statusText, { fontSize: 16 }]}>Attendance Marked</Text>
                  </View>
                ) : (
                  <Text style={styles.qrNote}>Present this QR code to mark your attendance</Text>
                )}
              </View>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  header: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerTitle: {
    ...typography.h2,
    color: colors.text,
  },
  headerSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  tabsContainer: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.sm,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: colors.primary,
  },
  tabText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: '600',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: spacing.md,
  },
  eventCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
    elevation: 2,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  eventTitle: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
    marginRight: spacing.sm,
  },
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
    gap: 4,
  },
  statusText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: '600',
  },
  registeredDate: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  attendanceTime: {
    ...typography.bodySmall,
    color: colors.success,
    marginBottom: spacing.sm,
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
    backgroundColor: colors.surface,
    gap: spacing.xs,
  },
  actionButtonText: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    ...typography.h3,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  emptySubtext: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    width: '100%',
    maxWidth: 400,
  },
  closeButton: {
    alignSelf: 'flex-end',
    padding: spacing.sm,
  },
  qrContainer: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
  },
  qrTitle: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  qrSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  qrCodeContainer: {
    padding: spacing.lg,
    backgroundColor: colors.white,
    borderRadius: borderRadius.md,
    marginVertical: spacing.md,
    elevation: 4,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  qrNote: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.md,
  },
});