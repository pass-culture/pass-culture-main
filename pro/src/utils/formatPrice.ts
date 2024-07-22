// New 2023 standard options that should be available in TypeScript ^5.5
// At this moment, VSCode's TypeScript version is still ^5.4
// (See: https://github.com/microsoft/TypeScript/issues/56269)
import { isError } from 'apiClient/helpers'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

type ResolvedNumberFormatOptions = Intl.NumberFormatOptions & {
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
}

export function formatPrice(
  price: number,
  options?: ResolvedNumberFormatOptions
) {
  let formattedPrice = ''
  try {
    formattedPrice = Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      ...options,
    }).format(price)
  } catch (e) {
    // Safari 14.1.2 throws an exception here.
    if (
      isError(e) &&
      e.message.includes(
        'Failed to initialize NumberFormat since used feature is not supported in the linked ICU version'
      )
    ) {
      formattedPrice =
        price
          .toFixed(2)
          .replace(/\d(?=(\d{3})+\.)/g, '$& ') // space after each group of 3
          .replace('.', ',') + ' €'
    } else {
      sendSentryCustomError(e)
    }
  }
  return formattedPrice
}
