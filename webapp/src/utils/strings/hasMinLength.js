import isString from './isString'

const hasMinLength = (value, min) => {
  if (!isString(value) || typeof min !== 'number') return false
  return value.length >= min
}

export default hasMinLength
