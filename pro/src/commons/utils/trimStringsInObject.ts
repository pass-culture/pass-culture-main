import { isPlainObject } from './isPlainObject'

export const trimStringsInObject = <T extends Record<string, any>>(
  obj: T,
  visited = new Set<object>()
): T => {
  // handle circular references
  if (!isPlainObject(obj) || visited.has(obj)) {
    return obj
  }
  visited.add(obj)

  const result: any = Array.isArray(obj) ? [] : {}
  for (const key of Object.keys(obj) as Array<keyof T>) {
    if (typeof obj[key] === 'string') {
      result[key] = obj[key].trim()
    } else if (isPlainObject(obj[key])) {
      result[key] = trimStringsInObject(obj[key], visited)
    } else {
      result[key] = obj[key]
    }
  }

  return result
}
