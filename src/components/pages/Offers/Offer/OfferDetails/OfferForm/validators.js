export const isUrlValid = val => {
  /*eslint-disable-next-line no-useless-escape*/
  const urlRegex = '^(https?)://[^s$.?#].[^s]*'
  if (val === null || val === '') {
    return true
  }
  const isValid = val.match(urlRegex)
  return isValid
}
