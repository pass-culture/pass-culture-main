import { isString } from './isString'

export function hasUppercase(value) {
  if (!isString(value) || !value.trim().length) return false
  return /[A-Z]/.test(value)
}

export default hasUppercase
