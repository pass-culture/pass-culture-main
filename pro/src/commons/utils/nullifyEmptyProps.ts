/**
 * We shouldn't need such a utility since filters and forms should handle values via null instead of empty strings,
 * but until we refactor everything, this utility help us centralize the logic.
 *
 */
export const nullifyEmptyProps = <T extends Record<string, unknown>>(
  obj: T
): T => {
  const result: Record<string, unknown> = structuredClone(obj)

  Object.keys(result).forEach((key) => {
    if (
      (typeof result[key] === 'string' && result[key].trim() === '') ||
      (Array.isArray(result[key]) && result[key].length === 0)
    ) {
      result[key] = null
    }
  })

  return result as T
}
