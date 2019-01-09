import { strings } from './strings'
import { isEmpty } from '../../../utils/strings'

export const validateMatchingFields = (
  value,
  mainvalue,
  matchingErrorMessage = strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM
) => {
  if (!mainvalue) return undefined
  if (!value || isEmpty(value)) return strings.DEFAULT_REQUIRED_ERROR
  const isMatchingConfirm = value && mainvalue === value
  if (isMatchingConfirm) return undefined
  return matchingErrorMessage
}

export default validateMatchingFields
