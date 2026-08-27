export type ResolvedNumberFormatOptions = Intl.NumberFormatOptions & {
  roundingPriority?: 'auto' | 'morePrecision' | 'lessPrecision'
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
  trailingZeroDisplay?: 'auto' | 'stripIfInteger'
}

export function formatPrice(
  price: number,
  options?: ResolvedNumberFormatOptions
) {
  return Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    ...options,
  })
    .format(price)
    .replace(/^([+-])/, '$1 ') // space after sign (ex: - 10,00 €)
}
