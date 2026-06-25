import { doesUserPreferReducedMotion } from '@/commons/utils/windowMatchMedia'

export const scrollToTop = () => {
  const scrollBehavior = doesUserPreferReducedMotion() ? 'auto' : 'smooth'
  document
    .getElementById('content-wrapper')
    ?.scrollTo({ top: 0, behavior: scrollBehavior })
}
