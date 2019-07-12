import isEqual from 'lodash.isequal'

const sortNumber = (a, b) => {
  if (a > b) return 1
  if (a < b) return -1
  return 0
}

// DEMO -> https://jsperf.com/es6-array-unique/1
const uniqueFilter = entries => entries.filter((elem, pos, arr) => arr.indexOf(elem) === pos)

const isValidType = value =>
  (typeof value === 'string' || typeof value === 'number') && (value || value >= 0)

const valueToNumber = v => {
  const isString = typeof v === 'string'
  return (!isString && v) || parseFloat(v, 10)
}

const valueToPrice = value => {
  if (value === 0) return '0'
  return (value && `${value.toString().replace('.', ',')}`) || ''
}

const parsePriceArray = value => {
  let result = (Array.isArray(value) && value) || [value]
  result = result.filter(isValidType).map(valueToNumber)
  result = uniqueFilter(result).sort(sortNumber)
  if (!result || !result.length) return null
  if (result.length === 1) return [result[0]]
  return [result[0], result[result.length - 1]]
}

export const defaultOutputPriceFormatter = (pricesArray, devise) => {
  if (!pricesArray || !Array.isArray(pricesArray) || !pricesArray.length) return '--'
  const space = '\u0020'
  const arrow = '\u2192'
  const spacedArrowSplitter = `${space}${arrow}${space}`
  const result = pricesArray.join(spacedArrowSplitter) || ''
  return `${result}\u0020${devise}`
}

export const priceIsDefined = value => {
  const isDefined =
    value !== null && value !== 'null' && !(value instanceof Error) && typeof value !== 'undefined'
  return isDefined
}

export const getDisplayPrice = (value, freeValue = null, formatterFunc = null, devise = '€') => {
  const isDefined = priceIsDefined(value)
  if (!isDefined) return ''

  const isFree = isEqual(value, 0) || isEqual(value, [0])
  if (isFree && freeValue) return freeValue

  const parsedPrices = parsePriceArray(value)
  if (!parsedPrices) return ''

  const pricesWithComma = parsedPrices.map(v => valueToPrice(v))

  const useDefaultFormatter = Boolean(!formatterFunc || typeof formatterFunc !== 'function')

  if (!useDefaultFormatter) return formatterFunc(pricesWithComma, devise)
  return defaultOutputPriceFormatter(pricesWithComma, devise)
}

export default getDisplayPrice
