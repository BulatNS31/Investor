export type NavIconName =
  | 'home' | 'building' | 'globe' | 'factory' | 'bar-chart' | 'line-chart'
  | 'info' | 'database' | 'book' | 'mail' | 'layout' | 'file-text'
  | 'users' | 'history' | 'settings'

export type NavItem = {
  label: string
  to: string
  icon: NavIconName
  children?: NavItem[]
}

export type NavSection = {
  label: string
  items: NavItem[]
}

export const siteNav: NavSection[] = [
  {
    label: 'Основное',
    items: [
      { label: 'Главная', to: '/', icon: 'home' },
      { label: 'Компании', to: '/companies', icon: 'building' },
      {
        label: 'Экономика',
        to: '/economy',
        icon: 'globe',
        children: [
          { label: 'Обзор', to: '/economy', icon: 'globe' },
          { label: 'ВВП', to: '/economy/gdp', icon: 'globe' },
          { label: 'Инфляция', to: '/economy/inflation', icon: 'globe' },
          { label: 'Ключевая ставка', to: '/economy/key-rate', icon: 'globe' },
          { label: 'Валютные курсы', to: '/economy/exchange-rates', icon: 'globe' },
          { label: 'Безработица', to: '/economy/unemployment', icon: 'globe' },
          { label: 'Госдолг', to: '/economy/public-debt', icon: 'globe' },
          { label: 'Промышленное производство', to: '/economy/industrial-production', icon: 'globe' },
        ],
      },
      { label: 'Отрасли', to: '/industries', icon: 'factory' },
      { label: 'Статистика', to: '/statistics', icon: 'bar-chart' },
      { label: 'Аналитика', to: '/analytics', icon: 'line-chart' },
    ],
  },
  {
    label: 'О проекте',
    items: [
      { label: 'О платформе', to: '/about', icon: 'info' },
      { label: 'Источники данных', to: '/about/sources', icon: 'database' },
      { label: 'Методология', to: '/about/methodology', icon: 'book' },
      { label: 'Контакты', to: '/about/contacts', icon: 'mail' },
    ],
  },
]

export const adminNav: NavSection[] = [
  {
    label: 'Управление',
    items: [
      { label: 'Дашборд', to: '/admin', icon: 'layout' },
      { label: 'Статьи', to: '/admin/articles', icon: 'file-text' },
      { label: 'Компании', to: '/admin/companies', icon: 'building' },
      { label: 'Отрасли', to: '/admin/industries', icon: 'factory' },
      { label: 'Показатели', to: '/admin/indicators', icon: 'line-chart' },
      { label: 'Статистика', to: '/admin/statistics', icon: 'bar-chart' },
      { label: 'Источники', to: '/admin/sources', icon: 'database' },
      { label: 'Пользователи', to: '/admin/users', icon: 'users' },
      { label: 'История изменений', to: '/admin/history', icon: 'history' },
      { label: 'Настройки сайта', to: '/admin/settings', icon: 'settings' },
    ],
  },
]
