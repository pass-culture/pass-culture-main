import { string } from "yup"

export const validatePhone = val => {
  const phoneRegex = /^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$/
  if (val && !phoneRegex.test(val)) {
    return 'Ce numéro de téléphone n’est pas valide merci de fournir un numéro de téléphone sans espaces'
  }
}

export const validateEmail = async val => {
  const isValid = await string().email().isValid(val)
  if (!isValid) {
    return 'Votre email n’est pas valide'
  }
}

export const validateUrl = async val => {
  const isValid = await string().url().isValid(val)
  if (!isValid) {
    return 'L’URL renseignée n’est pas valide'
  }
}
