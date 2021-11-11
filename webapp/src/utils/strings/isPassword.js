import isString from './isString'
import hasNumber from './hasNumber'
import hasMinLength from './hasMinLength'
import hasUppercase from './hasUppercase'
import hasLowercase from './hasLowercase'

const isPassword = (value, count = 12) =>
  value &&
  isString(value) &&
  hasMinLength(value, count) &&
  hasUppercase(value) &&
  hasLowercase(value) &&
  // l'ancien mot de passe durant la beta
  // ne contiennait pas caractere speciaux
  // hasSpecialChars(value) &&
  hasNumber(value)

export default isPassword
