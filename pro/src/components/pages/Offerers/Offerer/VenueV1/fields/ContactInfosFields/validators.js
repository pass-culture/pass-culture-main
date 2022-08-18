import { string } from 'yup'

import { urlRegex } from 'core/shared'

import { parseAndValidateFrenchPhoneNumber } from './utils'

export const validatePhone = phone => {
  if (!phone) {
    return
  }
  try {
    parseAndValidateFrenchPhoneNumber(phone)
  } catch (err) {
    return err
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

export const validateUrl = async url => {
  if (!url) {
    return
  }
  if (!urlRegex.test(url)) {
    return 'L’URL renseignée n’est pas valide'
  }
}
