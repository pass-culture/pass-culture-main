import { formatPrice, type ResolvedNumberFormatOptions } from './formatPrice'

const DEFAULT_PACIFIC_FRANC_TO_EURO_RATE = 0.00838

export function formatPacificFranc(
  amount: number,
  options?: ResolvedNumberFormatOptions
): string {
  const price = `${formatPrice(amount, options)
    .replace(/,\d*/, '')
    .replace(/\u202f/g, ' ')
    .replace(/\s€/g, '')} F`
  return price
}

export const convertEuroToPacificFranc = (priceInEuro: number): number => {
  let result = priceInEuro / DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
  result = Math.floor(result * 100) / 100

  result = Math.round(result / 5) * 5

  return result
}

export const convertPacificFrancToEuro = (
  priceInPacificFranc: number
): number => {
  let result = priceInPacificFranc * DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
  result = Math.floor(result * 100) / 100

  return result
}
