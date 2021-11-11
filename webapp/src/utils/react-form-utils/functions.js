export const capitalize = (string = '') => {
  return string ? `${string[0].toUpperCase()}${string.slice(1)}` : string
}

function pluralizeWord(string, number, pluralizeWith = 's') {
  let plural
  let singular
  const lastLetter = string.slice(-1)[0]
  if (lastLetter === 's' || lastLetter === 'x') {
    singular = string.slice(0, -1)
    plural = string
  } else {
    singular = string
    plural = `${string}${pluralizeWith}`
  }
  return number > 1 ? plural : singular
}

function pluralizeString(string, number, pluralizeWith) {
  return string
    .split(' ')
    .map(w => pluralizeWord(w, number, pluralizeWith))
    .join(' ')
}

export const pluralize = (number, string, pluralizeWith) => {
  if (typeof number === 'string' && typeof string === 'number') {
    // arguments are in the other way round, don't write number
    return pluralizeString(number, string, pluralizeWith)
  }
  return `${number} ${pluralizeString(string, number, pluralizeWith)}`
}

export const getCanSubmit = config => {
  if (!config) {
    throw new Error('getCanSubmit: Missing arguments')
  }
  const { isLoading, ...reactFinalFormProps } = config
  // https://github.com/final-form/final-form#formstate
  const {
    dirtySinceLastSubmit,
    hasSubmitErrors,
    hasValidationErrors,
    pristine,
  } = reactFinalFormProps

  const canSubmit =
    !isLoading &&
    ((!pristine && !hasSubmitErrors && !hasValidationErrors) ||
      (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit))

  return canSubmit
}

export const parseSubmitErrors = errors =>
  Object.keys(errors).reduce((acc, key) => {
    // FIXME -> test avec un array d'erreurs
    // a deplacer dans un tests unitaires
    // const err = errors[key].concat('toto')
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})
