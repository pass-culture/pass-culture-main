import { string } from 'yup'

export const isUrlValid = val => {
  const urlRegex = new RegExp(
    /*eslint-disable-next-line no-useless-escape*/
    /^(?:http(s)?:\/\/)[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:\/?#[\]@%!\$&'\(\)\*\+,;=.]+$/
  )
  if (val === null || val === '') {
    return true
  }
  return urlRegex.test(val)
}

export const isUrlWithStringInterpolationValid = val => {
  const urlRegex = new RegExp(
    /*eslint-disable-next-line no-useless-escape*/
    /^(?:http(s)?:\/\/)[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:\/?#[{}\]@%!\$&'\(\)\*\+,;=.]+$/
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
