import { string } from 'yup'

export const isUrlValid = val => {
  const urlRegex = new RegExp(
    /*eslint-disable-next-line no-useless-escape*/
    /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)(([a-z0-9]+([\-\.\.-\.@_a-z0-9]+)*\.[a-z]{2,5})|((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d))(:[0-9]{1,5})?\S*?$/,
    'i'
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
