import strings from './strings'
import isEmpty from '../../../utils/strings/isEmpty'

const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return strings.DEFAULT_REQUIRED_ERROR
}

export default validateRequiredField
