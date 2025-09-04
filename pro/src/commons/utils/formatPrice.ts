// New 2023 standard options that should be available in TypeScript ^5.5
// At this moment, VSCode's TypeScript version is still ^5.4
// (See: https://github.com/microsoft/TypeScript/issues/56269)
import { isError } from '@/apiClient/helpers'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'

import type { CurrencyCode } from '../core/shared/types'

export type ResolvedNumberFormatOptions = Intl.NumberFormatOptions & {
  roundingPriority?: 'auto' | 'morePrecision' | 'lessPrecision' | undefined
  roundingIncrement?:
    | 1
    | 2
    | 5
    | 10
    | 20
    | 25
    | 50
    | 100
    | 200
    | 250
    | 500
    | 1000
    | 2000
    | 2500
    | 5000
    | undefined
  roundingMode?:
    | 'ceil'
    | 'floor'
    | 'expand'
    | 'trunc'
    | 'halfCeil'
    | 'halfFloor'
    | 'halfExpand'
    | 'halfTrunc'
    | 'halfEven'
    | undefined
  trailingZeroDisplay?: 'auto' | 'stripIfInteger' | undefined
  currency?: CurrencyCode
}

export function formatPrice(
  price: number,
  options?: ResolvedNumberFormatOptions
) {
  switch (options?.currency) {
    case 'EUR':
      return formatPriceEuro(price, options ?? {})
    case 'XPF':
      return formatPriceXpf(price, options ?? {})
    default:
      throw new Error(`Currency ${options?.currency} is not supported.`)
  }
}

function isNumberFormatSupported() {
  try {
    new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(1234.5)
    return true
  } catch (err) {
    if (
      isError(err) &&
      err.message.includes(
        'Failed to initialize NumberFormat since used feature is not supported in the linked ICU version'
      )
    ) {
      return false
    }
    sendSentryCustomError(err)
    return false
  }
}

export function formatPriceEuro(
  price: number,
  options: ResolvedNumberFormatOptions
) {
  if (isNumberFormatSupported()) {
    return Intl.NumberFormat('fr-FR', {
      style: 'currency',
      ...options,
      currency: 'EUR',
    }).format(price)
  }
  return (
    price
      .toFixed(2)
      .replace(/\d(?=(\d{3})+\.)/g, '$&\u202f') // space after each group of 3
      .replace('.', ',') + '\xa0€'
  )
}

export function formatPriceXpf(
  price: number,
  options: ResolvedNumberFormatOptions
) {
  if (isNumberFormatSupported()) {
    return Intl.NumberFormat('fr-FR', {
      style: 'currency',
      ...options,
      maximumFractionDigits: 0,
      minimumFractionDigits: 0,
      currency: 'XPF',
    })
      .format(price)
      .replace('FCFP', 'F')
  }
  return (
    price
      .toFixed(2)
      .replace(/\d(?=(\d{3})+\.)/g, '$&\u202f') // space after each group of 3
      .replace(/\.\d*/, ',') + '\xa0F'
  )
}
