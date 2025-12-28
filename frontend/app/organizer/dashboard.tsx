import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
  Modal,
  ScrollView,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAuth, useApi } from '../../context/AuthContext';
import { colors, spacing, borderRadius, typography } from '../theme';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { format } from 'date-fns';

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  venue: string;
  fee: number;
  college: string;
  category: string;
  current_registrations: number;
  max_participants?: number;
}

export default function OrganizerDashboard() {
  const { user, logout } = useAuth();
  const api = useApi();
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    venue: '',
    fee: '',
    category: 'General',
    max_participants: '',
  });

  useEffect(() => {
    fetchMyEvents();
  }, []);

  const fetchMyEvents = async () => {
    try {
      const response = await api.get('/events/organizer/my-events');
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchMyEvents();
  };

  const handleCreateEvent = async () => {
    if (!formData.title || !formData.description || !formData.date || !formData.venue) {
      Alert.alert('Error', 'Please fill all required fields');
      return;
    }

    setCreating(true);
    try {
      await api.post('/events', {
        title: formData.title,
        description: formData.description,
        date: new Date(formData.date).toISOString(),
        venue: formData.venue,
        fee: parseFloat(formData.fee) || 0,
        category: formData.category,
        college: user?.college || '',
        max_participants: formData.max_participants ? parseInt(formData.max_participants) : null,
      });

      Alert.alert('Success', 'Event created successfully!');
      setShowCreateModal(false);
      setFormData({
        title: '',
        description: '',
        date: '',
        venue: '',
        fee: '',
        category: 'General',
        max_participants: '',
      });
      fetchMyEvents();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create event');
    } finally {
      setCreating(false);
    }
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
            await logout();
            router.replace('/');
          },
        },
      ]
    );
  };

  const renderEvent = ({ item }: { item: Event }) => {
    const eventDate = new Date(item.date);
    
    return (
      <View style={styles.eventCard}>
        <View style={styles.eventHeader}>
          <Text style={styles.eventTitle}>{item.title}</Text>
          <View style={[styles.badge, { backgroundColor: colors.primary }]}>
            <Text style={styles.badgeText}>{item.category}</Text>
          </View>
        </View>
        
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
            <Ionicons name="people" size={16} color={colors.accent} />
            <Text style={styles.detailText}>
              {item.current_registrations}{item.max_participants ? `/${item.max_participants}` : ''} registered
            </Text>
          </View>
        </View>
        
        <View style={styles.actions}>
          <TouchableOpacity 
            style={styles.actionBtn}
            onPress={() => router.push(`/organizer/qr-scanner?eventId=${item.id}`)}
          >
            <Ionicons name="qr-code-outline" size={18} color={colors.secondary} />
            <Text style={styles.actionText}>Scan QR</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionBtn}>
            <Ionicons name="list" size={18} color={colors.primary} />
            <Text style={styles.actionText}>View List</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Organizer Dashboard</Text>
          <Text style={styles.headerSubtitle}>{user?.name}</Text>
        </View>
        <TouchableOpacity onPress={handleLogout}>
          <Ionicons name="log-out" size={24} color={colors.error} />
        </TouchableOpacity>
      </View>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{events.length}</Text>
          <Text style={styles.statLabel}>Total Events</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {events.reduce((sum, e) => sum + e.current_registrations, 0)}
          </Text>
          <Text style={styles.statLabel}>Total Registrations</Text>
        </View>
      </View>

      {/* Create Event Button */}
      <TouchableOpacity 
        style={styles.createButton}
        onPress={() => setShowCreateModal(true)}
      >
        <Ionicons name="add-circle" size={24} color={colors.white} />
        <Text style={styles.createButtonText}>Create New Event</Text>
      </TouchableOpacity>

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
              <Text style={styles.emptyText}>No events yet</Text>
              <Text style={styles.emptySubtext}>Create your first event!</Text>
            </View>
          }
        />
      )}

      {/* Create Event Modal */}
      <Modal
        visible={showCreateModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowCreateModal(false)}
      >
        <KeyboardAvoidingView 
          style={styles.modalOverlay}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Create New Event</Text>
              <TouchableOpacity onPress={() => setShowCreateModal(false)}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <ScrollView showsVerticalScrollIndicator={false}>
              <TextInput
                style={styles.input}
                placeholder="Event Title *"
                value={formData.title}
                onChangeText={(text) => setFormData({ ...formData, title: text })}
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={[styles.input, styles.textArea]}
                placeholder="Description *"
                value={formData.description}
                onChangeText={(text) => setFormData({ ...formData, description: text })}
                multiline
                numberOfLines={4}
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Date (YYYY-MM-DD) *"
                value={formData.date}
                onChangeText={(text) => setFormData({ ...formData, date: text })}
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Venue *"
                value={formData.venue}
                onChangeText={(text) => setFormData({ ...formData, venue: text })}
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Registration Fee (0 for free)"
                value={formData.fee}
                onChangeText={(text) => setFormData({ ...formData, fee: text })}
                keyboardType="number-pad"
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Category"
                value={formData.category}
                onChangeText={(text) => setFormData({ ...formData, category: text })}
                placeholderTextColor={colors.textSecondary}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Max Participants (optional)"
                value={formData.max_participants}
                onChangeText={(text) => setFormData({ ...formData, max_participants: text })}
                keyboardType="number-pad"
                placeholderTextColor={colors.textSecondary}
              />
              
              <TouchableOpacity 
                style={[styles.submitButton, creating && styles.disabledButton]}
                onPress={handleCreateEvent}
                disabled={creating}
              >
                {creating ? (
                  <ActivityIndicator color={colors.white} />
                ) : (
                  <Text style={styles.submitButtonText}>Create Event</Text>
                )}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  statsContainer: {
    flexDirection: 'row',
    padding: spacing.md,
    gap: spacing.md,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.white,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  statNumber: {
    ...typography.h1,
    color: colors.primary,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  createButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    margin: spacing.md,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    gap: spacing.sm,
  },
  createButtonText: {
    ...typography.h3,
    color: colors.white,
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
  badge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  badgeText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: '600',
  },
  eventDescription: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  eventDetails: {
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailText: {
    ...typography.bodySmall,
    color: colors.text,
    marginLeft: spacing.sm,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
  },
  actionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.sm,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    gap: spacing.xs,
  },
  actionText: {
    ...typography.bodySmall,
    color: colors.text,
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
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  modalTitle: {
    ...typography.h2,
    color: colors.text,
  },
  input: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
    ...typography.body,
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: colors.primary,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginTop: spacing.md,
    marginBottom: spacing.xl,
  },
  disabledButton: {
    opacity: 0.6,
  },
  submitButtonText: {
    ...typography.h3,
    color: colors.white,
    textAlign: 'center',
  },
});