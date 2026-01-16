import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  RefreshControl,
  Alert,
  ActivityIndicator,
  Modal,
  ScrollView,
} from 'react-native';
import { useAuth, useApi } from '../../../context/AuthContext';
import { colors, spacing, borderRadius, typography } from '../../../theme';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { format } from 'date-fns';
import QRCode from 'react-native-qrcode-svg';

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  venue: string;
  fee: number;
  college: string;
  category: string;
  organizer_name: string;
  current_registrations: number;
  max_participants?: number;
}

export default function Discover() {
  const { user, logout } = useAuth();
  const api = useApi();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [showQRModal, setShowQRModal] = useState(false);
  
  const [dashboard, setDashboard] = useState({
    total_events_registered: 0,
    attended_events: 0,
    certificates_earned: 0,
    upcoming_events: 0,
  });

  useEffect(() => {
    fetchEvents();
    fetchDashboard();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await api.get('/events', {
        params: { search: searchQuery },
      });
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/dashboard/student');
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const handleSearch = () => {
    setLoading(true);
    fetchEvents();
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchEvents();
    fetchDashboard();
  };

  const handleEventPress = (event: Event) => {
    setSelectedEvent(event);
    setShowEventModal(true);
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await logout();
            } catch (error) {
              Alert.alert('Error', 'Failed to logout');
            }
          },
        },
      ]
    );
  };

  const handleRegister = async () => {
    if (!selectedEvent) return;

    setRegistering(true);
    try {
      const response = await api.post('/registrations', {
        event_id: selectedEvent.id,
      });
      
      setQrCode(response.data.qr_code_data);
      setShowEventModal(false);
      setShowQRModal(true);
      fetchDashboard();
      
      Alert.alert(
        'Success!',
        'You have successfully registered for the event. Your QR code is ready!',
        [{ text: 'View QR Code', onPress: () => setShowQRModal(true) }]
      );
    } catch (error: any) {
      Alert.alert('Registration Failed', error.response?.data?.detail || 'Please try again');
    } finally {
      setRegistering(false);
    }
  };

  const renderEvent = ({ item }: { item: Event }) => {
    const eventDate = new Date(item.date);
    const isPast = eventDate < new Date();
    
    return (
      <TouchableOpacity 
        style={styles.eventCard}
        onPress={() => handleEventPress(item)}
      >
        <View style={styles.eventHeader}>
          <View style={[styles.categoryBadge, { backgroundColor: colors.primary }]}>
            <Text style={styles.categoryText}>{item.category}</Text>
          </View>
          {item.fee === 0 && (
            <View style={[styles.freeBadge, { backgroundColor: colors.success }]}>
              <Text style={styles.freeText}>FREE</Text>
            </View>
          )}
        </View>
        
        <Text style={styles.eventTitle}>{item.title}</Text>
        <Text style={styles.eventDescription} numberOfLines={2}>
          {item.description}
        </Text>
        
        <View style={styles.eventDetails}>
          <View style={styles.detailRow}>
            <Ionicons name="calendar" size={16} color={colors.primary} />
            <Text style={styles.detailText}>
              {format(eventDate, 'MMM dd, yyyy')}
            </Text>
          </View>
          
          <View style={styles.detailRow}>
            <Ionicons name="location" size={16} color={colors.secondary} />
            <Text style={styles.detailText}>{item.venue}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Ionicons name="school" size={16} color={colors.accent} />
            <Text style={styles.detailText}>{item.college}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Ionicons name="people" size={16} color={colors.textSecondary} />
            <Text style={styles.detailText}>
              {item.current_registrations}{item.max_participants ? `/${item.max_participants}` : ''} registered
            </Text>
          </View>
        </View>
        
        {item.fee > 0 && (
          <View style={styles.feeContainer}>
            <Text style={styles.feeText}>₹{item.fee}</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Discover Events</Text>
          <Text style={styles.headerSubtitle}>Hello, {user?.name}!</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutIconButton}>
          <Ionicons name="log-out" size={24} color={colors.error} />
        </TouchableOpacity>
      </View>

      {/* Stats Cards */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: colors.primary }]}>
          <Ionicons name="calendar" size={24} color={colors.white} />
          <Text style={styles.statNumber}>{dashboard.total_events_registered}</Text>
          <Text style={styles.statLabel}>Registered</Text>
        </View>
        
        <View style={[styles.statCard, { backgroundColor: colors.secondary }]}>
          <Ionicons name="checkmark-circle" size={24} color={colors.white} />
          <Text style={styles.statNumber}>{dashboard.attended_events}</Text>
          <Text style={styles.statLabel}>Attended</Text>
        </View>
        
        <View style={[styles.statCard, { backgroundColor: colors.accent }]}>
          <Ionicons name="trophy" size={24} color={colors.white} />
          <Text style={styles.statNumber}>{dashboard.certificates_earned}</Text>
          <Text style={styles.statLabel}>Certificates</Text>
        </View>
        
        <View style={[styles.statCard, { backgroundColor: colors.success }]}>
          <Ionicons name="time" size={24} color={colors.white} />
          <Text style={styles.statNumber}>{dashboard.upcoming_events}</Text>
          <Text style={styles.statLabel}>Upcoming</Text>
        </View>
      </ScrollView>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color={colors.textSecondary} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search events..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
          placeholderTextColor={colors.textSecondary}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => {
            setSearchQuery('');
            handleSearch();
          }}>
            <Ionicons name="close-circle" size={20} color={colors.textSecondary} />
          </TouchableOpacity>
        )}
      </View>

      {/* Events List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={events}
          renderItem={renderEvent}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} colors={[colors.primary]} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="calendar-outline" size={64} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No events found</Text>
              <Text style={styles.emptySubtext}>Check back later for new events!</Text>
            </View>
          }
        />
      )}

      {/* Event Details Modal */}
      <Modal
        visible={showEventModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowEventModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <TouchableOpacity 
              style={styles.closeButton}
              onPress={() => setShowEventModal(false)}
            >
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
            
            {selectedEvent && (
              <ScrollView showsVerticalScrollIndicator={false}>
                <Text style={styles.modalTitle}>{selectedEvent.title}</Text>
                
                <View style={styles.modalBadgeContainer}>
                  <View style={[styles.categoryBadge, { backgroundColor: colors.primary }]}>
                    <Text style={styles.categoryText}>{selectedEvent.category}</Text>
                  </View>
                  {selectedEvent.fee === 0 && (
                    <View style={[styles.freeBadge, { backgroundColor: colors.success }]}>
                      <Text style={styles.freeText}>FREE</Text>
                    </View>
                  )}
                </View>
                
                <Text style={styles.modalDescription}>{selectedEvent.description}</Text>
                
                <View style={styles.modalDetailsContainer}>
                  <View style={styles.modalDetailRow}>
                    <Ionicons name="calendar" size={20} color={colors.primary} />
                    <View style={styles.modalDetailContent}>
                      <Text style={styles.modalDetailLabel}>Date & Time</Text>
                      <Text style={styles.modalDetailValue}>
                        {format(new Date(selectedEvent.date), 'MMMM dd, yyyy')}
                      </Text>
                    </View>
                  </View>
                  
                  <View style={styles.modalDetailRow}>
                    <Ionicons name="location" size={20} color={colors.secondary} />
                    <View style={styles.modalDetailContent}>
                      <Text style={styles.modalDetailLabel}>Venue</Text>
                      <Text style={styles.modalDetailValue}>{selectedEvent.venue}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.modalDetailRow}>
                    <Ionicons name="school" size={20} color={colors.accent} />
                    <View style={styles.modalDetailContent}>
                      <Text style={styles.modalDetailLabel}>Organized By</Text>
                      <Text style={styles.modalDetailValue}>{selectedEvent.organizer_name}</Text>
                      <Text style={styles.modalDetailSubValue}>{selectedEvent.college}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.modalDetailRow}>
                    <Ionicons name="people" size={20} color={colors.textSecondary} />
                    <View style={styles.modalDetailContent}>
                      <Text style={styles.modalDetailLabel}>Registrations</Text>
                      <Text style={styles.modalDetailValue}>
                        {selectedEvent.current_registrations}{selectedEvent.max_participants ? `/${selectedEvent.max_participants}` : ''}
                      </Text>
                    </View>
                  </View>
                  
                  {selectedEvent.fee > 0 && (
                    <View style={styles.modalDetailRow}>
                      <Ionicons name="cash" size={20} color={colors.success} />
                      <View style={styles.modalDetailContent}>
                        <Text style={styles.modalDetailLabel}>Registration Fee</Text>
                        <Text style={styles.modalDetailValue}>₹{selectedEvent.fee}</Text>
                      </View>
                    </View>
                  )}
                </View>
                
                <TouchableOpacity 
                  style={[styles.registerButton, registering && styles.disabledButton]}
                  onPress={handleRegister}
                  disabled={registering}
                >
                  {registering ? (
                    <ActivityIndicator color={colors.white} />
                  ) : (
                    <>
                      <Ionicons name="checkmark-circle" size={20} color={colors.white} />
                      <Text style={styles.registerButtonText}>Register for Event</Text>
                    </>
                  )}
                </TouchableOpacity>
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>

      {/* QR Code Modal */}
      <Modal
        visible={showQRModal}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setShowQRModal(false)}
      >
        <View style={styles.qrModalOverlay}>
          <View style={styles.qrModalContent}>
            <TouchableOpacity 
              style={styles.qrCloseButton}
              onPress={() => setShowQRModal(false)}
            >
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
            
            <View style={styles.qrContainer}>
              <Ionicons name="checkmark-circle" size={64} color={colors.success} style={{ marginBottom: 16 }} />
              <Text style={styles.qrTitle}>Registration Successful!</Text>
              <Text style={styles.qrSubtitle}>Show this QR code at the event</Text>
              
              {qrCode && (
                <View style={styles.qrCodeContainer}>
                  <QRCode
                    value={qrCode}
                    size={200}
                    color={colors.text}
                    backgroundColor={colors.white}
                  />
                </View>
              )}
              
              <Text style={styles.qrNote}>Save this QR code or find it in "My Events"</Text>
              
              <TouchableOpacity 
                style={styles.qrDoneButton}
                onPress={() => setShowQRModal(false)}
              >
                <Text style={styles.qrDoneButtonText}>Done</Text>
              </TouchableOpacity>
            </View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logoutIconButton: {
    padding: spacing.sm,
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
  statsContainer: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    backgroundColor: colors.white,
  },
  statCard: {
    width: 120,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    marginRight: spacing.md,
    alignItems: 'center',
  },
  statNumber: {
    ...typography.h2,
    color: colors.white,
    marginTop: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: colors.white,
    marginTop: spacing.xs,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    margin: spacing.md,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  searchIcon: {
    marginRight: spacing.sm,
  },
  searchInput: {
    flex: 1,
    padding: spacing.md,
    ...typography.body,
    color: colors.text,
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
    marginBottom: spacing.sm,
  },
  categoryBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  categoryText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: '600',
  },
  freeBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  freeText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: 'bold',
  },
  eventTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  eventDescription: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  eventDetails: {
    gap: spacing.xs,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  detailText: {
    ...typography.bodySmall,
    color: colors.text,
    marginLeft: spacing.sm,
  },
  feeContainer: {
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  feeText: {
    ...typography.h3,
    color: colors.primary,
    textAlign: 'right',
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
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: colors.white,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: spacing.lg,
    maxHeight: '90%',
  },
  closeButton: {
    alignSelf: 'flex-end',
    padding: spacing.sm,
  },
  modalTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.md,
  },
  modalBadgeContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  modalDescription: {
    ...typography.body,
    color: colors.text,
    marginBottom: spacing.lg,
    lineHeight: 24,
  },
  modalDetailsContainer: {
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  modalDetailRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  modalDetailContent: {
    marginLeft: spacing.md,
    flex: 1,
  },
  modalDetailLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  modalDetailValue: {
    ...typography.body,
    color: colors.text,
    fontWeight: '600',
  },
  modalDetailSubValue: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  registerButton: {
    backgroundColor: colors.primary,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.md,
    borderRadius: borderRadius.md,
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  disabledButton: {
    opacity: 0.6,
  },
  registerButtonText: {
    ...typography.h3,
    color: colors.white,
  },
  qrModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  qrModalContent: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    width: '100%',
    maxWidth: 400,
  },
  qrCloseButton: {
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
    marginVertical: spacing.lg,
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
  qrDoneButton: {
    backgroundColor: colors.primary,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    width: '100%',
    marginTop: spacing.lg,
  },
  qrDoneButtonText: {
    ...typography.h3,
    color: colors.white,
    textAlign: 'center',
  },
});
