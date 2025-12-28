import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../context/AuthContext';
import { colors, spacing, borderRadius, typography } from './theme';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

export default function Index() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) {
      // Navigate based on role
      switch (user.role) {
        case 'student':
          router.replace('/student/(tabs)');
          break;
        case 'organizer':
          router.replace('/organizer/dashboard');
          break;
        case 'admin':
          router.replace('/admin/dashboard');
          break;
      }
    }
  }, [user, loading]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header with Logo */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Image 
            source={require('../assets/images/logo.png')} 
            style={styles.logoImage}
            resizeMode="contain"
          />
          <Text style={styles.appName}>JoinUp</Text>
        </View>
        <Text style={styles.tagline}>Your College Events, Digitized</Text>
      </View>

      {/* Role Selection */}
      <ScrollView 
        style={styles.content}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>Welcome! Choose Your Role</Text>
        
        <TouchableOpacity 
          style={[styles.roleCard, { backgroundColor: colors.primary }]}
          onPress={() => router.push('/auth/role-selection?role=student')}
        >
          <View style={styles.roleIcon}>
            <Ionicons name="school" size={36} color={colors.white} />
          </View>
          <Text style={styles.roleTitle}>Student</Text>
          <Text style={styles.roleDescription}>
            Discover and register for inter-college events
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.roleCard, { backgroundColor: colors.secondary }]}
          onPress={() => router.push('/auth/role-selection?role=organizer')}
        >
          <View style={styles.roleIcon}>
            <Ionicons name="business" size={36} color={colors.white} />
          </View>
          <Text style={styles.roleTitle}>University / Club</Text>
          <Text style={styles.roleDescription}>
            Organize events and manage registrations
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.roleCard, { backgroundColor: colors.accent }]}
          onPress={() => router.push('/auth/role-selection?role=admin')}
        >
          <View style={styles.roleIcon}>
            <Ionicons name="shield-checkmark" size={36} color={colors.white} />
          </View>
          <Text style={styles.roleTitle}>Admin</Text>
          <Text style={styles.roleDescription}>
            Manage users and oversee platform
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  loadingText: {
    ...typography.body,
    textAlign: 'center',
    marginTop: 200,
  },
  header: {
    backgroundColor: colors.accent,
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: spacing.lg,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  logoIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  appName: {
    ...typography.h1,
    color: colors.white,
    fontSize: 42,
  },
  tagline: {
    ...typography.body,
    color: colors.white,
    textAlign: 'center',
    opacity: 0.9,
  },
  content: {
    flex: 1,
    padding: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  roleCard: {
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    alignItems: 'center',
    elevation: 4,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  roleIcon: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  roleTitle: {
    ...typography.h3,
    color: colors.white,
    marginBottom: spacing.sm,
  },
  roleDescription: {
    ...typography.bodySmall,
    color: colors.white,
    textAlign: 'center',
    opacity: 0.9,
  },
});