import { Outlet, useLocation } from 'react-router-dom'
import { AppShell } from './AppShell'
import { siteNav } from '../navigation/nav.config'

export default function SiteLayout() {
  const location = useLocation()
  const isAdmin = location.pathname.startsWith('/admin')
  return <AppShell nav={siteNav} variant="site" isAdmin={isAdmin}><Outlet /></AppShell>
}