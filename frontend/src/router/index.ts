import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy loaded components
const Home = () => import('@/views/Home.vue')
const Login = () => import('@/views/auth/Login.vue')
const RegisterVolunteer = () => import('@/views/auth/RegisterVolunteer.vue')
const RegisterOrganization = () => import('@/views/auth/RegisterOrganization.vue')
const ForgotPassword = () => import('@/views/auth/ForgotPassword.vue')
const ResetPassword = () => import('@/views/auth/ResetPassword.vue')

const ProjectsList = () => import('@/views/projects/ProjectsList.vue')
const ProjectDetail = () => import('@/views/projects/ProjectDetail.vue')
const CreateProject = () => import('@/views/projects/CreateProject.vue')
const EditProject = () => import('@/views/projects/EditProject.vue')

const NewsList = () => import('@/views/news/NewsList.vue')
const NewsDetail = () => import('@/views/news/NewsDetail.vue')

const VolunteerDashboard = () => import('@/views/dashboard/VolunteerDashboard.vue')
const OrganizationDashboard = () => import('@/views/dashboard/OrganizationDashboard.vue')
const AdminDashboard = () => import('@/views/dashboard/AdminDashboard.vue')
const ModeratorDashboard = () => import('@/views/dashboard/ModeratorDashboard.vue')

const Profile = () => import('@/views/profile/Profile.vue')
const MyApplications = () => import('@/views/applications/MyApplications.vue')
const OrganizationApplications = () => import('@/views/applications/OrganizationApplications.vue')

const VolunteersTable = () => import('@/views/volunteers/VolunteersTable.vue')

const Notifications = () => import('@/views/notifications/Notifications.vue')
const Reports = () => import('@/views/reports/Reports.vue')
const CreateReport = () => import('@/views/reports/CreateReport.vue')

const NotFound = () => import('@/views/NotFound.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public routes
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { title: 'Главная' }
    },
    {
      path: '/projects',
      name: 'ProjectsList',
      component: ProjectsList,
      meta: { title: 'Проекты' }
    },
    {
      path: '/projects/:id',
      name: 'ProjectDetail',
      component: ProjectDetail,
      meta: { title: 'Детали проекта' }
    },
    {
      path: '/news',
      name: 'NewsList',
      component: NewsList,
      meta: { title: 'Новости' }
    },
    {
      path: '/news/:slug',
      name: 'NewsDetail',
      component: NewsDetail,
      meta: { title: 'Новость' }
    },

    // Auth routes
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { title: 'Вход', guest: true }
    },
    {
      path: '/register/volunteer',
      name: 'RegisterVolunteer',
      component: RegisterVolunteer,
      meta: { title: 'Регистрация волонтера', guest: true }
    },
    {
      path: '/register/organization',
      name: 'RegisterOrganization',
      component: RegisterOrganization,
      meta: { title: 'Регистрация организации', guest: true }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPassword,
      meta: { title: 'Восстановление пароля', guest: true }
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPassword,
      meta: { title: 'Сброс пароля', guest: true }
    },

    // Protected routes
    {
      path: '/dashboard',
      name: 'Dashboard',
      meta: { title: 'Личный кабинет', requiresAuth: true },
      redirect: () => {
        const authStore = useAuthStore()
        const role = authStore.user?.role
        if (role === 'organization') return '/dashboard/organization'
        if (role === 'admin') return '/dashboard/admin'
        if (role === 'moderator') return '/dashboard/moderator'
        return '/dashboard/volunteer'
      }
    },
    {
      path: '/dashboard/volunteer',
      name: 'VolunteerDashboard',
      component: VolunteerDashboard,
      meta: { title: 'Личный кабинет волонтера', requiresAuth: true, roles: ['volunteer'] }
    },
    {
      path: '/dashboard/organization',
      name: 'OrganizationDashboard',
      component: OrganizationDashboard,
      meta: { title: 'Личный кабинет организации', requiresAuth: true, roles: ['organization'] }
    },
    {
      path: '/dashboard/admin',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { title: 'Админ панель', requiresAuth: true, roles: ['admin'] }
    },
    {
      path: '/dashboard/moderator',
      name: 'ModeratorDashboard',
      component: ModeratorDashboard,
      meta: { title: 'Панель модератора', requiresAuth: true, roles: ['moderator'] }
    },

    // Profile
    {
      path: '/profile',
      name: 'Profile',
      component: Profile,
      meta: { title: 'Профиль', requiresAuth: true }
    },

    // Applications
    {
      path: '/applications/my',
      name: 'MyApplications',
      component: MyApplications,
      meta: { title: 'Мои заявки', requiresAuth: true, roles: ['volunteer'] }
    },
    {
      path: '/applications/organization',
      name: 'OrganizationApplications',
      component: OrganizationApplications,
      meta: { title: 'Заявки на проекты', requiresAuth: true, roles: ['organization'] }
    },

    // Project management
    {
      path: '/projects/create',
      name: 'CreateProject',
      component: CreateProject,
      meta: { title: 'Создать проект', requiresAuth: true, roles: ['organization'] }
    },
    {
      path: '/projects/:id/edit',
      name: 'EditProject',
      component: EditProject,
      meta: { title: 'Редактировать проект', requiresAuth: true, roles: ['organization'] }
    },

    // Volunteers table (admin/moderator only) — Block 6
    {
      path: '/volunteers',
      name: 'VolunteersTable',
      component: VolunteersTable,
      meta: { title: 'Волонтёры', requiresAuth: true, roles: ['admin', 'moderator'] }
    },

    // Notifications
    {
      path: '/notifications',
      name: 'Notifications',
      component: Notifications,
      meta: { title: 'Уведомления', requiresAuth: true }
    },

    // Reports
    {
      path: '/reports',
      name: 'Reports',
      component: Reports,
      meta: { title: 'Отчеты', requiresAuth: true, roles: ['organization', 'admin'] }
    },
    {
      path: '/reports/create',
      name: 'CreateReport',
      component: CreateReport,
      meta: { title: 'Создать отчет', requiresAuth: true, roles: ['organization'] }
    },

    // 404
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound,
      meta: { title: 'Страница не найдена' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth if not already done
  if (!authStore.user && localStorage.getItem('access_token')) {
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route is for guests only
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  // Check role-based access
  if (to.meta.roles && authStore.user && !to.meta.roles.includes(authStore.user.role)) {
    // Redirect to appropriate dashboard based on user role
    switch (authStore.user.role) {
      case 'volunteer':
        next({ name: 'VolunteerDashboard' })
        break
      case 'organization':
        next({ name: 'OrganizationDashboard' })
        break
      case 'admin':
        next({ name: 'AdminDashboard' })
        break
      case 'moderator':
        next({ name: 'ModeratorDashboard' })
        break
      default:
        next({ name: 'Home' })
    }
    return
  }

  next()
})

// Update page title
router.afterEach((to) => {
  const baseTitle = 'Волонтерская платформа'
  document.title = to.meta.title ? `${to.meta.title} - ${baseTitle}` : baseTitle
})

export default router
