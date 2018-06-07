export function capitalize(word) { return `${word[0].toUpperCase()}${word.slice(1)}`}

export function removeWhitespaces(word) { return word.trim().replace(/\s/g, '') }