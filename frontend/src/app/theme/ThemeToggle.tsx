import { Monitor, Moon, Sun } from 'lucide-react'
import { useTheme, type ThemePreference } from './ThemeProvider'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const Icon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor
  const next: Record<ThemePreference, ThemePreference> = {
    light: 'dark',
    dark: 'system',
    system: 'light',
  }
  const labels: Record<ThemePreference, string> = {
    light: 'Светлая тема',
    dark: 'Тёмная тема',
    system: 'Системная тема',
  }

  return (
    <button
      type="button"
      className="glass-pill flex size-10 items-center justify-center rounded-full text-[var(--text-primary)]"
      aria-label={`Тема: ${labels[theme]}. Переключить тему`}
      aria-pressed={theme === 'dark'}
      title={labels[theme]}
      onClick={() => setTheme(next[theme])}
    >
      <Icon size={18} aria-hidden="true" />
    </button>
  )
}
