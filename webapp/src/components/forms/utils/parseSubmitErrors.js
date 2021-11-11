const parseSubmitErrors = errors =>
  Object.keys(errors).reduce((acc, key) => {
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})

export default parseSubmitErrors
