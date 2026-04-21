// User types
export interface User {
  id: number
  email: string
  username: string
  role: 'volunteer' | 'organization' | 'admin'
  phone: string
  avatar?: string
  date_joined: string
  is_active: boolean
  volunteer_profile?: VolunteerProfile
  organization_profile?: OrganizationProfile
}

export interface VolunteerProfile {
  first_name: string
  last_name: string
  birth_date?: string
  gender: string
  city: string
  region: string
  skills: string[]
  interests: string[]
  volunteer_hours: number
  average_rating?: number
}

export interface VolunteerCertificate {
  id: number
  title: string
  description: string
  file: string
  project?: number
  project_title?: string
  issued_by: string
  issued_at?: string
  created_at: string
}

export interface OrganizationProfile {
  name: string
  organization_type: string
  description: string
  website?: string
  phone: string
  address: string
  city: string
  region: string
}

// Project types
export interface Project {
  id: number
  title: string
  description: string
  category: Category
  format: 'online' | 'offline' | 'hybrid'
  region?: Region
  start_date?: string
  end_date?: string
  volunteers_needed: number
  status: 'active' | 'draft' | 'completed' | 'cancelled'
  organization_name?: string
  volunteers_count: number
  volunteers_remaining: number
  created_at: string
  image?: string
  contact_info?: string
  requirements?: string
}

export interface Category {
  id: number
  name: string
  description: string
  created_at: string
}

export interface Region {
  id: number
  name: string
  code: string
}

// Project participant (after close) — Block 5
export interface ProjectParticipant {
  volunteer_id: number
  application_id: number
  username: string
  name: string
  email: string
  avatar: string | null
  hours_committed: number
  total_hours: number
  is_banned: boolean
  has_certificate: boolean
}

// Application types
export interface Application {
  id: number
  volunteer: User
  project: Project
  status: 'pending' | 'approved' | 'rejected' | 'cancelled'
  cover_letter: string
  hours_committed: number
  created_at: string
  updated_at: string
  reviewed_by?: User
  reviewed_at?: string
  review_comment?: string
}

// News types
export interface News {
  id: number
  title: string
  slug: string
  content: string
  excerpt: string
  category: 'general' | 'events' | 'announcements' | 'success_stories'
  category_display: string
  status: 'draft' | 'published' | 'archived'
  status_display: string
  reading_time: number
  image?: string
  views_count: number
  author_name: string
  published_at?: string
  created_at: string
  updated_at: string
}

// Statistics types
export interface Statistics {
  users: {
    total: number
    volunteers: number
    organizations: number
    admins: number
    active: number
    recent: number
  }
  projects: {
    total: number
    active: number
    draft: number
    completed: number
    cancelled: number
    recent: number
    total_volunteers_needed: number
  }
  applications: {
    total: number
    pending: number
    approved: number
    rejected: number
    cancelled: number
    recent: number
    total_hours: number
  }
  my_applications?: {
    total: number
    pending: number
    approved: number
    rejected: number
    total_hours: number
  }
  recommended_projects?: Project[]
  achievements?: {
    total_projects: number
    total_hours: number
    average_rating: number
    longest_streak: number
    diversity_score: number
  }
}

// Notification types
export interface Notification {
  id: number
  recipient: User
  sender?: User
  notification_type: 'system' | 'application' | 'project' | 'news' | 'report'
  title: string
  message: string
  is_read: boolean
  created_at: string
  content_type?: string
  object_id?: number
}

export interface NotificationPreference {
  user: User
  email_new_applications: boolean
  email_project_updates: boolean
  email_news: boolean
  email_reports: boolean
  inapp_new_applications: boolean
  inapp_project_updates: boolean
  inapp_news: boolean
  inapp_reports: boolean
}

// Report types
export interface ProjectReport {
  id: number
  project: Project
  title: string
  description: string
  goals_achieved: string
  total_volunteers_participated: number
  total_volunteer_hours: number
  beneficiaries_count: number
  status: 'draft' | 'submitted' | 'approved' | 'rejected'
  created_at: string
  updated_at: string
  submitted_at?: string
  reviewed_by?: User
  reviewed_at?: string
  review_comment?: string
}

export interface VolunteerContribution {
  id: number
  report: ProjectReport
  volunteer: User
  hours_contributed: number
  contribution_description: string
  created_at: string
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  tokens: {
    refresh: string
    access: string
  }
}

export interface RegisterVolunteerRequest {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  phone?: string
  birth_date?: string
  gender?: string
  city?: string
  region?: string
  skills?: string[]
  interests?: string[]
}

export interface RegisterOrganizationRequest {
  email: string
  password: string
  password_confirm: string
  name: string
  organization_type: string
  description?: string
  website?: string
  phone?: string
  address?: string
  city?: string
  region?: string
}

// API Response types
export interface ApiResponse<T> {
  count?: number
  next?: string | null
  previous?: string | null
  results: T[]
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Form types
export interface ProjectFilters {
  search?: string
  category?: number
  region?: number
  format?: string
  status?: string
  start_date?: string
  end_date?: string
}

export interface ApplicationFilters {
  status?: string
  project?: number
  volunteer?: number
}
