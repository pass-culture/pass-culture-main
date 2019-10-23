import isString from './isString'

const hasNumber = value => {
  if (!isString(value) || !value.trim().length) return false
  return /[0-9]/.test(value)
}

export default hasNumber
