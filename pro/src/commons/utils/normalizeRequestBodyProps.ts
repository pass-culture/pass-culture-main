/**
 * Normalize a (POST, PATCH) request body object following these rules:
 * - `undefined` means that this field should not be changed.
 * - `null` means that this field should be set to null (= erased).
 * - An empty string value should be converted to `null` to effectively clear the field (= erased).
 */
export const normalizeRequestBodyProps = <T extends Record<string, unknown>>(
  object: T
): T => {
  const entries: [keyof T, unknown][] = Object.entries(object)
  const formattedEntries = entries
    .filter(([_key, value]) => value !== undefined)
    .map(([key, value]): [keyof T, unknown] => {
      if (typeof value === 'string') {
        const trimedValue = value.trim()
        return [key, trimedValue.length === 0 ? null : trimedValue]
      }

      return [key, value]
    })

  return Object.fromEntries(formattedEntries) as T
}
