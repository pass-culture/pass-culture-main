import type { CurrencyCode } from '../core/shared/types'

const DEFAULT_PACIFIC_FRANC_TO_EURO_RATE = 0.00838

export const convertPrice = (
  price: number,
  direction: { from?: CurrencyCode; to: CurrencyCode }
): number => {
  const currencyFrom = direction.from || 'EUR'
  const currencyTo = direction.to || 'EUR'

  if (currencyFrom === currencyTo) {
    return price
  }
  if (currencyFrom === 'EUR' && currencyTo === 'XPF') {
    return convertEurToXpf(price)
  }
  if (currencyFrom === 'XPF' && currencyTo === 'EUR') {
    return convertXpfToEur(price)
  }
  throw new Error(
    `Conversion from ${direction.from} to ${direction.to} is not supported.`
  )
}

// XPF
export const convertEurToXpf = (priceInEuro: number): number => {
  let result = priceInEuro / DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
  result = Math.floor(result * 100) / 100
  result = Math.round(result / 5) * 5 // rounding to the nearest 5 XPF

  return result
}

export const convertXpfToEur = (priceInPacificFranc: number): number => {
  let result = priceInPacificFranc * DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
  result = Math.floor(result * 100) / 100

  return result
}
// END XPF
