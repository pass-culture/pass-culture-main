export const toEnumOrNull = <T extends Record<string, string | number>>(
  value: unknown,
  enumObject: T
): T[keyof T] | null => {
  const enumValues = Object.values(enumObject) as Array<T[keyof T]>

  return enumValues.includes(value as T[keyof T]) ? (value as T[keyof T]) : null
}
