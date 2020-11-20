export const getRequestErrorStringFromErrors = errors => {
  if (errors instanceof Array) {
    return errors
      .map(error =>
        Object.keys(error)
          .map(key => error[key])
          .join(' ')
      )
      .join(' ')
  }

  if (errors instanceof Object) {
    return Object.keys(errors)
      .map(key => errors[key].map(error => error).join(' '))
      .join(' ')
  }

  return ''
}

export const queryStringToObject = (string = '') =>
  string &&
  string
    .replace(/^\??/, '')
    .split('&')
    .filter(el => el)
    .reduce((result, group) => {
      const [key, value] = group.split('=')
      return Object.assign({}, result, { [key]: value })
    }, {})
