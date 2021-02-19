export function getObjectWithMappedKeys(obj, keysMap) {
  const mappedObj = {}
  Object.keys(obj).forEach(objKey => {
    let mappedKey = objKey
    if (keysMap[objKey]) {
      mappedKey = keysMap[objKey]
    }
    mappedObj[mappedKey] = obj[objKey]
  })
  return mappedObj
}

export default getObjectWithMappedKeys
