function CloudSvg({ night = false }: { night?: boolean }) {
  const suffix = night ? 'night' : 'day'
  return (
    <svg
      viewBox="0 0 1600 900"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 h-full w-full"
      aria-hidden="true"
    >
      <defs>
        <filter id={`cloud-${suffix}`} x="-15%" y="-15%" width="130%" height="130%">
          <feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="5" seed={night ? 19 : 8} result="noise" />
          <feColorMatrix
            in="noise"
            type="matrix"
            values={night
              ? '0.55 0 0 0 0.18  0 0.68 0 0 0.25  0 0 0.78 0 0.36  0 0 0 1.9 -0.62'
              : '1 0 0 0 0.96  0 1 0 0 0.98  0 0 1 0 1  0 0 0 2.1 -0.72'}
            result="cloud"
          />
          <feGaussianBlur in="cloud" stdDeviation={night ? '9' : '12'} />
        </filter>
      </defs>
      <rect width="1600" height="900" filter={`url(#cloud-${suffix})`} fill={night ? '#a8bfd0' : '#ffffff'} />
    </svg>
  )
}

export function SkyBackground() {
  return (
    <div
      className="pointer-events-none fixed inset-0 -z-10 transform-gpu overflow-hidden"
      aria-hidden="true"
    >
      <div
        className="sky-day absolute inset-0 opacity-100 transition-opacity duration-400"
        style={{ background: 'linear-gradient(180deg, #2a6fb5 0%, #79add3 58%, #cfe6f7 100%), var(--sky-day-image)' }}
      >
        <CloudSvg />
      </div>
      <div
        className="sky-night absolute inset-0 opacity-0 transition-opacity duration-400 dark:opacity-100"
        style={{ background: 'linear-gradient(180deg, #050b1f 0%, #0b1b3a 58%, #14305a 100%), var(--sky-night-image)' }}
      >
        <CloudSvg night />
        <svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" className="absolute inset-0 h-full w-full opacity-60">
          <g fill="#d7e8f2">
            <circle cx="120" cy="110" r="1.2" /><circle cx="280" cy="72" r="0.8" />
            <circle cx="460" cy="150" r="1" /><circle cx="650" cy="92" r="1.3" />
            <circle cx="830" cy="178" r="0.8" /><circle cx="1010" cy="68" r="1" />
            <circle cx="1190" cy="135" r="1.2" /><circle cx="1380" cy="88" r="0.8" />
            <circle cx="1510" cy="205" r="1" /><circle cx="360" cy="260" r="0.7" />
            <circle cx="720" cy="230" r="0.9" /><circle cx="1300" cy="310" r="0.7" />
          </g>
        </svg>
      </div>
      <div className="absolute inset-0" style={{ background: 'var(--sky-scrim)' }} />
    </div>
  )
}
