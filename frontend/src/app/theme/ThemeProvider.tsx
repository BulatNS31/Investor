import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'

type ThemeContextValue = {
  theme: ThemePreference
  setTheme: (theme: ThemePreference) => void
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: 'system',
  setTheme: () => undefined,
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemePreference>('system')

  useEffect(() => {
    try {
      const saved = localStorage.getItem('investor-theme')
      if (saved === 'light' || saved === 'dark' || saved === 'system') setThemeState(saved)
    } catch {
      // Storage is optional; the inline head script already handles first paint.
    }
  }, [])

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    let preference = theme
    try {
      const saved = localStorage.getItem('investor-theme')
      if (saved === 'light' || saved === 'dark' || saved === 'system') preference = saved
    } catch {}
    const apply = () => {
      const dark = preference === 'dark' || (preference === 'system' && media.matches)
      document.documentElement.classList.toggle('dark', dark)
      document.documentElement.style.colorScheme = dark ? 'dark' : 'light'
    }
    apply()
    try { localStorage.setItem('investor-theme', preference) } catch {}
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [theme])

  const value = useMemo(() => ({
    theme,
    setTheme: (next: ThemePreference) => {
      try { localStorage.setItem('investor-theme', next) } catch {}
      setThemeState(next)
    },
  }), [theme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  return useContext(ThemeContext)
}
