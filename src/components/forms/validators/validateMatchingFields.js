import { strings } from './strings'
import { isEmpty, isPassword } from '../../../utils/strings'

export const validateMatchingFields = (value, mainvalue) => {
  // si la valeur principale n'est pas un mot de passe
  // on ne renvoi pas d'erreur
  // l'erreur sera retournée par le champs principale
  // FIXME -> ici on est fortement lié à un input de type password
  // use solution serait peut être
  // de passer la function de test en callback ou functionnel
  if (!mainvalue || !isPassword(mainvalue)) return undefined
  if (!value || isEmpty(value)) return strings.DEFAULT_REQUIRED_ERROR
  const isMatchingConfirm = value && mainvalue === value
  if (isMatchingConfirm) return undefined
  return strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM
}

export default validateMatchingFields
