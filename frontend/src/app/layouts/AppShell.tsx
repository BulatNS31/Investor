import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Menu, X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import type { NavSection } from '../navigation/nav.config'
import { Sidebar } from './Sidebar'
import { SkyBackground } from './SkyBackground'
import { ThemeToggle } from '../theme/ThemeToggle'

function getPageName(nav: NavSection[], pathname: string) {
  for (const section of nav) {
    for (const item of section.items) {
      if (pathname === item.to) return item.label
      const child = item.children?.find((entry) => pathname === entry.to)
      if (child) return child.label
    }
  }
  if (pathname === '/search') return 'Поиск'
  return pathname.startsWith('/admin') ? 'Администрирование' : 'Investor'
}

export function AppShell({ nav, variant = 'site', children, isAdmin = false }: {
  nav: NavSection[]
  variant?: 'site' | 'admin'
  children?: ReactNode
  isAdmin?: boolean
}) {
  const [collapsed, setCollapsed] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const burgerRef = useRef<HTMLButtonElement>(null)
  const drawerRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  useEffect(() => {
    try { setCollapsed(localStorage.getItem('investor-sidebar-collapsed') === 'true') } catch {}
  }, [])

  useEffect(() => { setDrawerOpen(false) }, [location.pathname])

  useEffect(() => {
    if (!drawerOpen) return
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const timer = window.setTimeout(() => {
      const focusable = drawerRef.current?.querySelector<HTMLElement>('a, button, input, [tabindex]:not([tabindex="-1"])')
      focusable?.focus()
    }, 0)
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setDrawerOpen(false)
        burgerRef.current?.focus()
      }
      if (event.key === 'Tab' && drawerRef.current) {
        const items = Array.from(drawerRef.current.querySelectorAll<HTMLElement>('a, button, input, [tabindex]:not([tabindex="-1"])'))
          .filter((element) => !element.hasAttribute('disabled'))
        if (!items.length) return
        const first = items[0]
        const last = items[items.length - 1]
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault()
          first.focus()
        }
      }
    }
    document.addEventListener('keydown', handleKey)
    return () => {
      window.clearTimeout(timer)
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', handleKey)
    }
  }, [drawerOpen])

  const toggleCollapsed = () => {
    setCollapsed((current) => {
      const next = !current
      try { localStorage.setItem('investor-sidebar-collapsed', String(next)) } catch {}
      return next
    })
  }

  const closeDrawer = () => {
    setDrawerOpen(false)
    window.setTimeout(() => burgerRef.current?.focus(), 0)
  }

  return (
    <div className="min-h-screen text-[var(--text-primary)]">
      <SkyBackground />
      <a className="skip-link" href="#main-content">К содержимому</a>

      <div className="hidden lg:block">
        <div className="fixed left-3 top-3 z-30" style={{ width: collapsed ? 76 : 280 }}>
          <Sidebar nav={nav} variant={variant} collapsed={collapsed} onCollapse={toggleCollapsed} />
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button type="button" className="absolute inset-0 bg-[#050b1f]/45" aria-label="Закрыть меню" onClick={closeDrawer} />
          <div ref={drawerRef} className="absolute left-3 top-3 h-[calc(100vh-24px)] w-[280px] max-w-[calc(100vw-24px)]" role="dialog" aria-modal="true" aria-label="Меню навигации">
            <Sidebar nav={nav} variant={variant} collapsed={false} onCollapse={() => undefined} mobile onNavigate={closeDrawer} />
            <button type="button" className="glass-pill absolute right-3 top-3 flex size-9 items-center justify-center rounded-full" aria-label="Закрыть меню" onClick={closeDrawer}>
              <X size={18} aria-hidden="true" />
            </button>
          </div>
        </div>
      )}

      <div className={`relative min-h-screen ${collapsed ? 'lg:pl-[100px]' : 'lg:pl-[304px]'}`}>
        <header className="sticky top-3 z-20 mx-3 flex h-12 items-center justify-between lg:ml-0 lg:mr-4">
          <div className="glass-pill flex h-12 items-center gap-2 rounded-full px-2 pr-4">
            <button ref={burgerRef} type="button" className="flex size-10 items-center justify-center rounded-full lg:hidden" aria-label="Открыть меню" aria-expanded={drawerOpen} onClick={() => setDrawerOpen(true)}>
              <Menu size={20} aria-hidden="true" />
            </button>
            <span className="text-sm font-semibold">{getPageName(nav, location.pathname)}</span>
          </div>
          <div className="flex items-center gap-2">
            {variant === 'site' && isAdmin && (
              <Link to="/admin" className="glass-pill hidden h-10 items-center rounded-full px-4 text-sm font-semibold sm:flex">Админ-панель</Link>
            )}
            <ThemeToggle />
          </div>
        </header>

        <main id="main-content" className="mx-auto min-h-[calc(100vh-60px)] max-w-[1200px] px-3 pb-5 pt-5 sm:px-5 lg:px-6">
          {children}
          <footer className="glass mt-8 rounded-2xl px-5 py-4 text-sm text-[var(--text-secondary)]">
            Материалы носят информационный характер и не являются инвестиционной рекомендацией
          </footer>
        </main>
      </div>
    </div>
  )
}
