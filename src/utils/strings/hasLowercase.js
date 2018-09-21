import { isString } from './isString'

export const hasLowercase = value => {
  if (!isString(value) || !value.trim().length) return false
  return /[a-z]/.test(value)
}

export default hasLowercase
