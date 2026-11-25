import { Route, Routes, useLocation, useSearchParams } from 'react-router-dom'
import SiteLayout from './app/layouts/SiteLayout'
import AdminLayout from './app/layouts/AdminLayout'
import { GlassCard, BigNumber, Pill } from './app/layouts/ui'

const titles: Record<string, string> = {
  '/': 'Главная',
  '/companies': 'Компании',
  '/economy': 'Экономика',
  '/economy/gdp': 'ВВП',
  '/economy/inflation': 'Инфляция',
  '/economy/key-rate': 'Ключевая ставка',
  '/economy/exchange-rates': 'Валютные курсы',
  '/economy/unemployment': 'Безработица',
  '/economy/public-debt': 'Госдолг',
  '/economy/industrial-production': 'Промышленное производство',
  '/industries': 'Отрасли',
  '/statistics': 'Статистика',
  '/analytics': 'Аналитика',
  '/about': 'О платформе',
  '/about/sources': 'Источники данных',
  '/about/methodology': 'Методология',
  '/about/contacts': 'Контакты',
}

function Page() {
  const { pathname } = useLocation()
  const title = titles[pathname] || 'Раздел'
  return (
    <article>
      <h1 className="mb-6 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <GlassCard title="Обзор" action={<Pill>Актуально</Pill>}>
          <p className="text-[var(--text-secondary)]">Раздел «{title}» готов к наполнению данными платформы.</p>
        </GlassCard>
        <GlassCard title="Ключевой показатель">
          <BigNumber value={12.02} fractionDigits={2} suffix="%" />
        </GlassCard>
      </div>
    </article>
  )
}

function SearchPage() {
  const [params] = useSearchParams()
  return (
    <article>
      <h1 className="mb-6 text-3xl font-bold">Поиск</h1>
      <GlassCard title={params.get('q') ? `Результаты для «${params.get('q')}»` : 'Введите запрос'}>
        <p className="text-[var(--text-secondary)]">Поиск по компаниям, экономическим показателям и статьям.</p>
      </GlassCard>
    </article>
  )
}

function AdminPage() {
  const { pathname } = useLocation()
  const name = pathname === '/admin' ? 'Дашборд' : pathname.split('/').filter(Boolean).pop()
  return (
    <article>
      <h1 className="mb-6 text-3xl font-bold">{name}</h1>
      <GlassCard title="Панель управления">
        <p className="text-[var(--text-secondary)]">Раздел администрирования Investor.</p>
      </GlassCard>
    </article>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/admin/*" element={<AdminLayout />}>
        <Route path="*" element={<AdminPage />} />
      </Route>
      <Route element={<SiteLayout />}>
        <Route path="/search" element={<SearchPage />} />
        <Route path="*" element={<Page />} />
      </Route>
    </Routes>
  )
}
