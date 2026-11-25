import type { ReactNode } from 'react'

export function GlassCard({ title, action, children, padding = 'p-5', className = '' }: {
  title?: ReactNode
  action?: ReactNode
  children: ReactNode
  padding?: string
  className?: string
}) {
  return (
    <section className={`glass rounded-2xl ${padding} ${className}`}>
      {(title || action) && (
        <header className="mb-4 flex items-center justify-between gap-4">
          {title && <h2 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h2>}
          {action}
        </header>
      )}
      {children}
    </section>
  )
}

export function Pill({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={`glass-pill inline-flex items-center rounded-full px-3 py-1 text-sm ${className}`}>{children}</span>
}

export function BigNumber({ value, fractionDigits = 0, prefix = '', suffix = '' }: {
  value: number
  fractionDigits?: number
  prefix?: string
  suffix?: string
}) {
  const formatted = value.toFixed(fractionDigits)
  const [whole, fraction] = formatted.split('.')
  return (
    <span className="inline-flex items-baseline text-[var(--text-primary)]" aria-label={`${prefix}${formatted}${suffix}`}>
      {prefix && <span className="mr-1 text-[0.55em] font-semibold">{prefix}</span>}
      <span className="text-[1.5em] font-bold tracking-tight">{whole}</span>
      {fraction !== undefined && <span className="text-[0.75em] font-medium text-[var(--text-secondary)]">.{fraction}</span>}
      {suffix && <span className="ml-1 text-[0.55em] text-[var(--text-secondary)]">{suffix}</span>}
    </span>
  )
}
