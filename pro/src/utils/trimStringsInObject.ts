import { isPlainObject } from './isPlainObject'

export const trimStringsInObject = (obj: any, visited = new Set()) => {
  // handle circular references
  if (!isPlainObject(obj) || visited.has(obj)) {
    return obj
  }
  visited.add(obj)

  for (const key of Object.keys(obj)) {
    if (typeof obj[key] === 'string') {
      obj[key] = obj[key].trim()
    } else if (isPlainObject(obj[key])) {
      obj[key] = trimStringsInObject(obj[key], visited)
    }
  }

  return obj
}
