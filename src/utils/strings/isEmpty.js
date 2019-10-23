import isString from './isString'

const isEmpty = value => {
  if (!isString(value)) return false
  return value.trim().length === 0
}

export default isEmpty
