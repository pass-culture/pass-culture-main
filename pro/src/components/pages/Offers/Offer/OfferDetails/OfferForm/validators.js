import { string } from 'yup'

export const isUrlValid = val => {
  /*eslint-disable-next-line no-useless-escape*/
  const urlRegex = new RegExp(
    /^(http|https):\/\/([A-z0-9-_]+)\.([A-z0-9-_]{2,})/
  )
  if (val === null || val === '') {
    return true
  }
  return urlRegex.test(val)
}

export const isEmailValid = async val => {
  if (val === null || val === '') {
    return true
  }
  return await string().email().isValid(val)
}
