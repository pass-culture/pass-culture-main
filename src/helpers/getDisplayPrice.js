import isEqual from 'lodash.isequal'

const CURRENCY_SYMBOL = '€'

const valueToNumber = v => {
  const isString = typeof v === 'string'
  return (!isString && v) || parseFloat(v, 10)
}

const valueToPrice = value => {
  if (value === 0) return '0'
  return (value && `${value.toString().replace('.', ',')}`) || ''
}

const defaultOutputPriceFormatter = pricesArray => {
  const SPACE = '\u0020'
  const ARROW = '\u2192'
  const spacedArrowSplitter = `${SPACE}${ARROW}${SPACE}`

  const result = pricesArray.join(spacedArrowSplitter)
  return `${result}${SPACE}${CURRENCY_SYMBOL}`
}

export const priceIsDefined = value => {
  const isDefined =
    value !== null && value !== 'null' && !(value instanceof Error) && typeof value !== 'undefined'
  return isDefined
}

export const getDisplayPrice = (simplePriceOrPriceRange, freeValue = null) => {
  const priceRange = (Array.isArray(simplePriceOrPriceRange) && simplePriceOrPriceRange) || [
    simplePriceOrPriceRange,
  ]

  const parsedPrices = priceRange.map(valueToNumber)

  if (!parsedPrices.length) return ''

  const isFree = isEqual(priceRange, 0) || isEqual(priceRange, [0])
  if (isFree && freeValue) return freeValue

  const pricesWithComma = parsedPrices.map(v => valueToPrice(v))
  return defaultOutputPriceFormatter(pricesWithComma)
}

export default getDisplayPrice
