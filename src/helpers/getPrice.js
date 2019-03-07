// jest --env=jsdom ./src/helpers/tests/getPrice --watch
import isEqual from 'lodash.isequal'

const arrow = '\u2192 '

const sortNumber = (a, b) => {
  if (a > b) return 1
  if (a < b) return -1
  return 0
}

// DEMO -> https://jsperf.com/es6-array-unique/1
const uniqueFilter = entries =>
  entries.filter((elem, pos, arr) => arr.indexOf(elem) === pos)

const isValidType = value =>
  (typeof value === 'string' || typeof value === 'number') &&
  (value || value >= 0)

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

export const priceIsDefined = value => {
  const isDefined =
    value !== null &&
    value !== 'null' &&
    !(value instanceof Error) &&
    typeof value !== 'undefined'
  return isDefined
}

export const getPrice = (value, freeValue = null, devise = '€') => {
  const isDefined = priceIsDefined(value)
  if (!isDefined) return ''

  const isFree = isEqual(value, 0) || isEqual(value, [0])
  if (isFree && freeValue) return freeValue

  const array = parsePriceArray(value)
  if (!array) return ''

  const formatedDevise = array.map(v => valueToPrice(v)).join(` ${arrow}`) || ''
  return `${formatedDevise} ${devise}`
}

export default getPrice
