export function capitalize(word='') {
  return word
    ? `${word[0].toUpperCase()}${word.slice(1)}`
    : word
}

export function removeWhitespaces(word) {
  return word && word.trim().replace(/\s/g, '')
}

function pluralizeWord(singular, number) {
  return `${singular}${number > 1 ? 's' : ''}`
}

export function pluralize(number, singular) {
  if (typeof number === 'string' && typeof singular === 'number') {
    // arguments are in the other way round, don't write number
    return pluralizeWord(number, singular)
  }
  return `${number} ${pluralizeWord(singular, number)}`
}
