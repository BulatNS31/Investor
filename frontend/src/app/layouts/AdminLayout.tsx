import { Outlet } from 'react-router-dom'
import { AppShell } from './AppShell'
import { adminNav } from '../navigation/nav.config'

export default function AdminLayout() {
  return <AppShell nav={adminNav} variant="admin"><Outlet /></AppShell>
}