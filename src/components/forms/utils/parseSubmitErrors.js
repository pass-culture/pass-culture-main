const parseSubmitErrors = errors =>
  Object.keys(errors).reduce((acc, key) => {
    // FIXME -> test avec un array d'erreurs
    // a deplacer dans un tests unitaires
    // const err = errors[key].concat('toto')
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})

export default parseSubmitErrors
