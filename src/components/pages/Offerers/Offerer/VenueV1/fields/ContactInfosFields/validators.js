import { string } from 'yup'

export const validatePhone = val => {
  const phoneRegex = /^((\+)33|0)[1-9](\d{2}){4}$/
  if (val === null) {
    return
  }
  if (val && !phoneRegex.test(val)) {
    return 'Ce numéro de téléphone n’est pas valide merci de fournir un numéro de téléphone sans espaces'
  }
}

export const validateEmail = async val => {
  const isValid = await string().email().isValid(val)
  if (val === null) {
    return
  }
  if (!isValid) {
    return 'Votre email n’est pas valide'
  }
}

export const validateUrl = async val => {
  const isValid = await string().url().isValid(val)
  if (val === null) {
    return
  }
  if (!isValid) {
    return 'L’URL renseignée n’est pas valide'
  }
}
