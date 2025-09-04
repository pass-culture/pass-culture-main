import type { CurrencyCode } from '../core/shared/types'
import { useIsCaledonian } from './useIsCaledonian'

export const useCurrency = (): CurrencyCode => {
  const isCaledonian = useIsCaledonian()
  return isCaledonian ? 'XPF' : 'EUR'
}
