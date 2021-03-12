export const doesUserPreferReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches
