import strings from './strings'
import { checkIfEmailIsValid } from '../../pages/create-account/domain/checkIfEmailIsValid'

const validateEmailField = value => {
  if (checkIfEmailIsValid(value)) return undefined
  return strings.EMAIL_ERROR_MESSAGE
}

export default validateEmailField
