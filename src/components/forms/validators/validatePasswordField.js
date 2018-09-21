import { isPassword } from '../../../utils/strings'

const DEFAULT_ERROR_MESSAGE =
  'Le mot de passe doit contenir au minimum 12 caractères, un chiffre, une majuscule, une minuscule et un caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'

export const validatePasswordField = () => value => {
  if (isPassword(value)) return undefined
  return DEFAULT_ERROR_MESSAGE
}

export default validatePasswordField
