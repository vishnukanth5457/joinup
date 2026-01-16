import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useAuth, useApi } from '../../context/AuthContext';
import { colors, spacing, borderRadius, typography } from '../../theme';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

interface Analytics {
  total_events: number;
  total_registrations: number;
  total_attendees: number;
  upcoming_events: number;
  past_events: number;
  average_rating: number;
  top_events: Array<{
    id: string;
    title: string;
    registrations: number;
    rating: number;
  }>;
}

export default function OrganizerAnalytics() {
  const api = useApi();
  const router = useRouter();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/dashboard/organizer');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Analytics Dashboard</Text>
      </View>

      {/* Overview Cards */}
      <View style={styles.overviewGrid}>
        <View style={[styles.overviewCard, { backgroundColor: colors.primary }]}>
          <Ionicons name="calendar" size={32} color={colors.white} />
          <Text style={styles.overviewNumber}>{analytics?.total_events || 0}</Text>
          <Text style={styles.overviewLabel}>Total Events</Text>
        </View>

        <View style={[styles.overviewCard, { backgroundColor: colors.secondary }]}>
          <Ionicons name="people" size={32} color={colors.white} />
          <Text style={styles.overviewNumber}>{analytics?.total_registrations || 0}</Text>
          <Text style={styles.overviewLabel}>Registrations</Text>
        </View>

        <View style={[styles.overviewCard, { backgroundColor: colors.success }]}>
          <Ionicons name="checkmark-circle" size={32} color={colors.white} />
          <Text style={styles.overviewNumber}>{analytics?.total_attendees || 0}</Text>
          <Text style={styles.overviewLabel}>Attendees</Text>
        </View>

        <View style={[styles.overviewCard, { backgroundColor: colors.accent }]}>
          <Ionicons name="star" size={32} color={colors.white} />
          <Text style={styles.overviewNumber}>{analytics?.average_rating.toFixed(1) || 0}</Text>
          <Text style={styles.overviewLabel}>Avg Rating</Text>
        </View>
      </View>

      {/* Event Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Event Status</Text>
        <View style={styles.statusGrid}>
          <View style={styles.statusCard}>
            <Ionicons name="time" size={24} color={colors.warning} />
            <Text style={styles.statusNumber}>{analytics?.upcoming_events || 0}</Text>
            <Text style={styles.statusLabel}>Upcoming</Text>
          </View>

          <View style={styles.statusCard}>
            <Ionicons name="archive" size={24} color={colors.textSecondary} />
            <Text style={styles.statusNumber}>{analytics?.past_events || 0}</Text>
            <Text style={styles.statusLabel}>Past</Text>
          </View>
        </View>
      </View>

      {/* Top Performing Events */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Top Performing Events</Text>
        {analytics?.top_events.map((event, index) => (
          <View key={event.id} style={styles.topEventCard}>
            <View style={styles.rankBadge}>
              <Text style={styles.rankText}>#{index + 1}</Text>
            </View>
            <View style={styles.topEventContent}>
              <Text style={styles.topEventTitle}>{event.title}</Text>
              <View style={styles.topEventStats}>
                <View style={styles.topEventStat}>
                  <Ionicons name="people" size={16} color={colors.secondary} />
                  <Text style={styles.topEventStatText}>{event.registrations}</Text>
                </View>
                {event.rating > 0 && (
                  <View style={styles.topEventStat}>
                    <Ionicons name="star" size={16} color={colors.warning} />
                    <Text style={styles.topEventStatText}>{event.rating.toFixed(1)}</Text>
                  </View>
                )}
              </View>
            </View>
          </View>
        ))}
      </View>

      {/* Engagement Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Engagement Metrics</Text>
        <View style={styles.metricCard}>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Attendance Rate</Text>
            <Text style={styles.metricValue}>
              {analytics?.total_registrations > 0
                ? ((analytics.total_attendees / analytics.total_registrations) * 100).toFixed(1)
                : 0}
              %
            </Text>
          </View>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Avg Registrations/Event</Text>
            <Text style={styles.metricValue}>
              {analytics?.total_events > 0
                ? Math.round(analytics.total_registrations / analytics.total_events)
                : 0}
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    padding: spacing.lg,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    padding: spacing.sm,
    marginRight: spacing.md,
  },
  headerTitle: {
    ...typography.h2,
    color: colors.text,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: spacing.md,
    gap: spacing.md,
  },
  overviewCard: {
    width: '47%',
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    elevation: 2,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  overviewNumber: {
    ...typography.h1,
    color: colors.white,
    marginTop: spacing.sm,
  },
  overviewLabel: {
    ...typography.caption,
    color: colors.white,
    marginTop: spacing.xs,
  },
  section: {
    padding: spacing.lg,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.md,
  },
  statusGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  statusCard: {
    flex: 1,
    backgroundColor: colors.white,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  statusNumber: {
    ...typography.h2,
    color: colors.text,
    marginTop: spacing.sm,
  },
  statusLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  topEventCard: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
    elevation: 1,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  rankBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  rankText: {
    ...typography.body,
    color: colors.white,
    fontWeight: 'bold',
  },
  topEventContent: {
    flex: 1,
  },
  topEventTitle: {
    ...typography.body,
    color: colors.text,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  topEventStats: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  topEventStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  topEventStatText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  metricCard: {
    backgroundColor: colors.white,
    padding: spacing.md,
    borderRadius: borderRadius.md,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  metricLabel: {
    ...typography.body,
    color: colors.text,
  },
  metricValue: {
    ...typography.h3,
    color: colors.primary,
  },
});
