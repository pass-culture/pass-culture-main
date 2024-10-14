export const doesUserPreferReducedMotion = () =>
  /* istanbul ignore next: DEBT, TO FIX */
  window.matchMedia('(prefers-reduced-motion: reduce)').matches
