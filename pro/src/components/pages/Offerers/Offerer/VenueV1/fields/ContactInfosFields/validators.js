import { string } from 'yup'

import { urlRegex } from 'core/shared'
import { parseAndValidateFrenchPhoneNumber } from 'core/shared/utils/parseAndValidateFrenchPhoneNumber'

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
    return 'Veuillez renseigner un email valide'
  }
}

export const validateUrl = async url => {
  if (!url) {
    return
  }
  if (!urlRegex.test(url)) {
    return 'Veuillez renseigner une URL valide. Ex : https://exemple.com'
  }
}
