export const defaultFreeValue = 'Gratuit'

const priceIsDefined = value => {
  const isDefined =
    value !== null &&
    value !== 'null' &&
    !(value instanceof Error) &&
    typeof value !== 'undefined'
  return isDefined
}

const priceIsEmpty = value => {
  const isEmpty =
    (typeof value !== 'string' && typeof value !== 'number') ||
    (value && typeof value === 'string' && value.trim() === '') ||
    value === 0 ||
    !value
  return isEmpty
}

export const getPrice = (value, free = defaultFreeValue) => {
  const isDefined = priceIsDefined(value)
  if (!isDefined) return ''

  const isEmpty = priceIsEmpty(value)
  if (isEmpty) return free

  return (value && `${value.toString().replace('.', ',')}€`) || ''
}

export default getPrice
