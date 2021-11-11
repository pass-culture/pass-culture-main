export const removeDuplicatesObjects = a =>
  [...new Set(a.map(o => JSON.stringify(o)))].map(s => JSON.parse(s))

export const sortAlphabeticallyArrayOfObjectsByProperty = property => {
  return function(object, nextObject) {
    return object[property].localeCompare(nextObject[property])
  }
}
