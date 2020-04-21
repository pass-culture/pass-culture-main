export const pick = (object, keys) => {
  const result = {}
  keys.forEach(key => {
    if (object[key]) {
      result[key] = object[key]
    }
  })
  return result
}
