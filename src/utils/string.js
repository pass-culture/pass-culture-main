export function capitalize(string='') {
  return string
    ? `${string[0].toUpperCase()}${string.slice(1)}`
    : string
}

export function removeWhitespaces(string) {
  return string && string.trim().replace(/\s/g, '')
}

function pluralizeWord(string, number, pluralizeWith='s') {
  let singular, plural
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
  return string.split(' ').map(w => pluralizeWord(w, number, pluralizeWith)).join(' ')
}

export function pluralize(number, string, pluralizeWith) {
  if (typeof number === 'string' && typeof string === 'number') {
    // arguments are in the other way round, don't write number
    return pluralizeString(number, string, pluralizeWith)
  }
  return `${number} ${pluralizeString(string, number, pluralizeWith)}`
}

export function queryStringToObject(string='') {
  return string.replace(/^\??/, '').split('&').reduce((result, group) => {
    const [key, value] = group.split('=')
    return Object.assign({}, result, {[key]: value})
  }, {})
}