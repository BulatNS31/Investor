import { useEffect, useRef, useState, type FormEvent } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart3, BookOpen, Building2, ChevronDown, Database, Factory, FileText,
  Globe2, History, Home, Info, LayoutDashboard, LineChart, Mail, PanelLeft,
  Search, Settings, Sparkles, Users,
} from 'lucide-react'
import type { NavIconName, NavItem, NavSection } from '../navigation/nav.config'

const icons = {
  home: Home, building: Building2, globe: Globe2, factory: Factory,
  'bar-chart': BarChart3, 'line-chart': LineChart, info: Info, database: Database,
  book: BookOpen, mail: Mail, layout: LayoutDashboard, 'file-text': FileText,
  users: Users, history: History, settings: Settings,
} satisfies Record<NavIconName, typeof Home>

type SidebarProps = {
  nav: NavSection[]
  variant: 'site' | 'admin'
  collapsed: boolean
  onCollapse: () => void
  mobile?: boolean
  onNavigate?: () => void
}

function itemContainsPath(item: NavItem, pathname: string) {
  if (pathname === item.to) return true
  if (item.children?.some((child) => pathname === child.to)) return true
  return item.to !== '/' && pathname.startsWith(`${item.to}/`)
}

export function Sidebar({ nav, variant, collapsed, onCollapse, mobile = false, onNavigate }: SidebarProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({})
  const [flyout, setFlyout] = useState<string | null>(null)
  const firstLinkRef = useRef<HTMLAnchorElement>(null)

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('investor-open-groups') || '{}') as Record<string, boolean>
      setOpenGroups(saved)
    } catch {}
  }, [])

  useEffect(() => {
    setOpenGroups((current) => {
      const next = { ...current }
      nav.forEach((section) => section.items.forEach((item) => {
        if (item.children && itemContainsPath(item, location.pathname) && next[item.to] === undefined) next[item.to] = true
      }))
      return next
    })
  }, [location.pathname, nav])

  useEffect(() => {
    if (mobile) firstLinkRef.current?.focus()
  }, [mobile])

  const toggleGroup = (to: string) => {
    setOpenGroups((current) => {
      const next = { ...current, [to]: !current[to] }
      try { localStorage.setItem('investor-open-groups', JSON.stringify(next)) } catch {}
      return next
    })
  }

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const value = query.trim()
    if (value) navigate(`/search?q=${encodeURIComponent(value)}`)
  }

  const closeAfterNavigate = () => onNavigate?.()

  return (
    <aside
      className={`${mobile ? 'glass-strong' : 'glass-strong'} flex h-[calc(100vh-24px)] flex-col rounded-3xl px-3 py-4 transition-[width] duration-200`}
      style={{ width: collapsed && !mobile ? 76 : 280 }}
      aria-label="Основная навигация"
    >
      <div className="flex h-11 items-center justify-between px-1">
        <NavLink to={variant === 'admin' ? '/admin' : '/'} className="flex min-w-0 items-center gap-2.5" aria-label="Investor — на главную" onClick={closeAfterNavigate}>
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-[var(--accent)] text-[var(--text-on-accent)]">
            <LineChart size={20} aria-hidden="true" />
          </span>
          {(!collapsed || mobile) && <span className="text-lg font-bold tracking-tight">Investor</span>}
        </NavLink>
        {!mobile && (
          <button
            type="button"
            className="flex size-9 shrink-0 items-center justify-center rounded-full text-[var(--text-secondary)] hover:bg-[var(--accent-soft)]"
            onClick={onCollapse}
            aria-label={collapsed ? 'Развернуть боковую панель' : 'Свернуть боковую панель'}
            title={collapsed ? 'Развернуть' : 'Свернуть'}
            aria-pressed={collapsed}
          >
            <PanelLeft size={18} aria-hidden="true" />
          </button>
        )}
      </div>

      <form onSubmit={submit} className="mt-3" role="search">
        {collapsed && !mobile ? (
          <button type="button" className="mx-auto flex size-10 items-center justify-center rounded-full bg-[var(--glass-bg)]" aria-label="Поиск" title="Поиск" onClick={() => onCollapse()}>
            <Search size={18} aria-hidden="true" />
          </button>
        ) : (
          <label className="glass-pill flex h-11 items-center gap-2 rounded-full px-3">
            <Search size={17} className="shrink-0 text-[var(--text-secondary)]" aria-hidden="true" />
            <span className="sr-only">Поиск</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-[var(--text-secondary)]" placeholder="Поиск…" />
          </label>
        )}
      </form>

      <nav className="mt-4 flex-1 overflow-y-auto overscroll-contain px-0.5" aria-label={variant === 'admin' ? 'Навигация админ-панели' : 'Навигация по сайту'}>
        {nav.map((section) => (
          <section key={section.label} className="mb-4">
            {(!collapsed || mobile) && <h2 className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--text-secondary)]">{section.label}</h2>}
            <div className="space-y-1">
              {section.items.map((item, index) => {
                const Icon = icons[item.icon]
                const active = itemContainsPath(item, location.pathname)
                const open = Boolean(openGroups[item.to])
                if (item.children) {
                  return (
                    <div key={item.to} className="relative">
                      <button
                        ref={index === 0 ? firstLinkRef : undefined}
                        type="button"
                        className={`flex h-11 w-full items-center rounded-xl text-sm font-medium ${collapsed && !mobile ? 'justify-center' : 'gap-3 px-3'} ${active ? 'bg-[var(--active-bg)] text-[var(--active-text)] shadow-sm' : 'text-[var(--text-primary)] hover:bg-[var(--accent-soft)]'}`}
                        onClick={() => collapsed && !mobile ? setFlyout(flyout === item.to ? null : item.to) : toggleGroup(item.to)}
                        aria-expanded={collapsed && !mobile ? flyout === item.to : open}
                        aria-label={collapsed ? item.label : undefined}
                        title={collapsed ? item.label : undefined}
                      >
                        <Icon size={19} className="shrink-0" aria-hidden="true" />
                        {(!collapsed || mobile) && <>
                          <span className="flex-1 text-left">{item.label}</span>
                          <ChevronDown size={16} className={`transition-transform ${open ? 'rotate-180' : ''}`} aria-hidden="true" />
                        </>}
                      </button>
                      {collapsed && !mobile ? flyout === item.to && (
                        <div className="glass-strong absolute left-[68px] top-0 z-50 w-64 rounded-2xl p-2">
                          {item.children.map((child) => (
                            <NavLink key={child.to} to={child.to} end={child.to === '/economy'} className={({ isActive }) => `block rounded-xl px-3 py-2 text-sm ${isActive ? 'bg-[var(--active-bg)] text-[var(--active-text)]' : 'text-[var(--text-primary)] hover:bg-[var(--accent-soft)]'}`} onClick={closeAfterNavigate}>
                              {child.label}
                            </NavLink>
                          ))}
                        </div>
                      ) : (
                        <div className={`grid transition-[grid-template-rows] duration-200 ${open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
                          <div className="overflow-hidden">
                            <div className="relative ml-[21px] border-l border-[var(--glass-border)] py-1 pl-4">
                              {item.children.map((child) => (
                                <NavLink
                                  key={child.to}
                                  to={child.to}
                                  end={child.to === item.to}
                                  className={({ isActive }) => `block rounded-lg px-2 py-2 text-sm ${isActive ? 'font-semibold text-[var(--accent)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}`}
                                  onClick={closeAfterNavigate}
                                >
                                  {child.label}
                                </NavLink>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                }
                return (
                  <NavLink
                    key={item.to}
                    ref={index === 0 ? firstLinkRef : undefined}
                    to={item.to}
                    end={item.to === '/' || item.to === '/admin'}
                    aria-label={collapsed && !mobile ? item.label : undefined}
                    title={collapsed && !mobile ? item.label : undefined}
                    onClick={closeAfterNavigate}
                    className={({ isActive }) => `flex h-11 items-center rounded-xl text-sm font-medium ${collapsed && !mobile ? 'justify-center' : 'gap-3 px-3'} ${isActive ? 'bg-[var(--active-bg)] text-[var(--active-text)] shadow-sm' : 'text-[var(--text-primary)] hover:bg-[var(--accent-soft)]'}`}
                  >
                    <Icon size={19} className="shrink-0" aria-hidden="true" />
                    {(!collapsed || mobile) && <span>{item.label}</span>}
                  </NavLink>
                )
              })}
            </div>
          </section>
        ))}
      </nav>

      {variant === 'site' && (!collapsed || mobile) && (
        <NavLink to="/about" onClick={closeAfterNavigate} className="mt-2 rounded-3xl bg-gradient-to-br from-[#08705f] to-[#07463f] p-4 text-white shadow-lg">
          <div className="flex items-start gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-white text-[#08705f]"><Sparkles size={19} aria-hidden="true" /></span>
            <div>
              <div className="font-bold">Investor Pro</div>
              <div className="mt-1 text-xs leading-5 text-white/75">Расширенная аналитика, выгрузка данных и сравнения без ограничений</div>
            </div>
          </div>
          <span className="mt-3 block rounded-full bg-[#d3f2ea] py-2.5 text-center text-sm font-bold text-[#07463f]">Подробнее</span>
        </NavLink>
      )}
    </aside>
  )
}
