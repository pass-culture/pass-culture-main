import type { GetOfferLastProviderResponseModel } from '@/apiClient/v1'

import { CINEMA_PROVIDER_NAMES } from '../constants'

const normalizeProviderName = (providerName: string): string => {
  return providerName
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
}

/* istanbul ignore next: DEBT, TO FIX */
const isAllocineProviderName = (providerName: string | null): boolean => {
  if (providerName === null) {
    return false
  }
  return normalizeProviderName(providerName) === 'allocine'
}

/* istanbul ignore next: DEBT, TO FIX */
const isCinemaProviderName = (providerName: string | null): boolean => {
  return (
    providerName !== null &&
    CINEMA_PROVIDER_NAMES.includes(providerName.toLowerCase())
  )
}

/* istanbul ignore next: DEBT, TO FIX */
export const isAllocineProvider = (
  provider?: GetOfferLastProviderResponseModel | null
): boolean => {
  if (!provider) {
    return false
  }
  return isAllocineProviderName(provider.name)
}

/* istanbul ignore next: DEBT, TO FIX */
export const isCinemaProvider = (
  provider?: GetOfferLastProviderResponseModel | null
): boolean => {
  if (!provider) {
    return false
  }
  return isCinemaProviderName(provider.name)
}
