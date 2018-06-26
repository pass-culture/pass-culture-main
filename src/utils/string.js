export function capitalize(word='') {
  return word
    ? `${word[0].toUpperCase()}${word.slice(1)}`
    : word
}

export function removeWhitespaces(word) {
  return word && word.trim().replace(/\s/g, '')
}

function pluralizeWord(word, number, pluralizeWith='s') {
  let singular, plural
  const lastLetter = word.slice(-1)[0]
  if (lastLetter === 's' || lastLetter === 'x') {
    singular = word.slice(0, -1)
    plural = word
  } else {
    singular = word
    plural = `${word}${pluralizeWith}`
  }
  return number > 1 ? plural : singular
}

export function pluralize(number, word, pluralizeWith) {
  if (typeof number === 'string' && typeof word === 'number') {
    // arguments are in the other way round, don't write number
    return pluralizeWord(number, word, pluralizeWith)
  }
  return `${number} ${pluralizeWord(word, number, pluralizeWith)}`
}

export function queryStringToObject(string='') {
  return string.replace(/^\??/, '').split('&').reduce((result, group) => {
    const [key, value] = group.split('=')
    return Object.assign({}, result, {[key]: value})
  }, {})
}