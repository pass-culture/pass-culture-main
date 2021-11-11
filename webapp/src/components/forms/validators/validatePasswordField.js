import strings from './strings'
import isPassword from '../../../utils/strings/isPassword'

const validatePasswordField = value => {
  if (isPassword(value)) return undefined
  return strings.PASSWORD_ERROR_MESSAGE
}

export default validatePasswordField
