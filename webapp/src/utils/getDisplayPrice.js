const EURO_SYMBOL = '€'
const SPACE = '\u0020'
const NO_BREAK_SPACE = '\u00A0'
const RIGHTWARDS_ARROW = '\u2192'

const valueToNumber = value => {
  const isString = typeof value === 'string'
  return (!isString && value) || parseFloat(value, 10)
}

export const formatToFrenchDecimal = value => {
  if (value === 0) return '0'
  return (value && `${value.toString().replace('.', ',')}`) || ''
}

const formatPrice = prices => {
  const separator = `${SPACE}${RIGHTWARDS_ARROW}${SPACE}`

  const result = prices.join(separator)
  return `${result}${NO_BREAK_SPACE}${EURO_SYMBOL}`
}

export const priceIsDefined = value => {
  return (
    value !== null && value !== 'null' && !(value instanceof Error) && typeof value !== 'undefined'
  )
}

const getDisplayPrice = (simplePriceOrPriceRange, freeValue = null) => {
  const priceRange = Array.isArray(simplePriceOrPriceRange)
    ? simplePriceOrPriceRange
    : [simplePriceOrPriceRange]

  const parsedPrices = priceRange.map(valueToNumber)
  if (parsedPrices.length <= 0) return ''

  const isFree = priceRange.includes(0)
  if (isFree && freeValue) return freeValue

  const pricesWithComma = parsedPrices.map(value => formatToFrenchDecimal(value))
  return formatPrice(pricesWithComma)
}

export default getDisplayPrice
