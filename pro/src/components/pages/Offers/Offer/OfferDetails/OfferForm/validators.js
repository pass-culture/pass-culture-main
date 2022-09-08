import { string } from 'yup'

import { offerFormUrlRegex } from 'core/shared'

export const isUrlValid = val => {
  if (val === null || val === '') {
    return true
  }
  return offerFormUrlRegex.test(val)
}

export const isEmailValid = async val => {
  if (val === null || val === '') {
    return true
  }
  return await string().email().isValid(val)
}
