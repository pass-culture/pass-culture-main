const DEFAULT_PACIFIC_FRANC_TO_EURO_RATE = 0.00838

export function formatPacificFranc(amount: number): string {
  return `${amount.toLocaleString('fr-FR').replace(/\s/g, '')} F`
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
