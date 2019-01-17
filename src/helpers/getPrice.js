import isEqual from 'lodash.isequal'

const devise = '€'
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

const parsePriceArray = array => {
  let result = array.filter(isValidType).map(valueToNumber)
  result = uniqueFilter(result).sort(sortNumber)
  if (!result || !result.length) return null
  if (result.length === 1) return [result[0]]
  return [result[0], result[result.length - 1]]
}

const priceIsDefined = value => {
  const isDefined =
    value !== null &&
    value !== 'null' &&
    !(value instanceof Error) &&
    typeof value !== 'undefined'
  return isDefined
}

export const getPrice = value => {
  const isDefined = priceIsDefined(value)
  if (!isDefined) return ''

  const isFree = isEqual(value, [0])
  if (isFree) return 'Gratuit'

  let array = (Array.isArray(value) && value) || [value]

  array = parsePriceArray(array)

  if (!array) return ''

  const formatedDevise = array.map(v => valueToPrice(v)).join(` ${arrow}`) || ''
  return `${formatedDevise} ${devise}`
}

export default getPrice
