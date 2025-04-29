export function BackgroundGradientSVG() {
  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient
          id="background-gradient-1"
          gradientTransform="rotate(90)"
        >
          <stop offset="0%" stopColor="var(--color-background-brand-primary)" />
          <stop offset="100%" stopColor="var(--color-primary)" />
        </linearGradient>

        <linearGradient
          id="background-gradient-2"
          gradientTransform="rotate(90)"
        >
          <stop
            offset="30%"
            stopColor="var(--color-background-brand-primary)"
          />
          <stop offset="70%" stopColor="var(--color-primary)" />
        </linearGradient>
      </defs>
      <rect
        x="0"
        y="0"
        width="100"
        height="100"
        fill="url(#background-gradient-2)"
      />
      <path
        d="M 0 0 C 0 50 100 50 100 100 L 0 100 Z"
        fill="url(#background-gradient-1)"
      />
    </svg>
  )
}
