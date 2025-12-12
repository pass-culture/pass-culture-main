export const isPlainObject = (
  value: unknown
): value is Record<string, unknown> => {
  if (!value || typeof value !== 'object') {
    return false
  }
  const prototype = Object.getPrototypeOf(value)
  return (
    prototype === null ||
    (value.constructor === Object && prototype === Object.getPrototypeOf({}))
  )
}
