export const toNumberOrNull = (
  value: string | number | null | undefined
): number | null => {
  if (typeof value === 'number') {
    return value
  }

  if (value === undefined || value === null || value.trim() === '') {
    return null
  }

  const valueAsNumber = Number(value)

  return Number.isNaN(valueAsNumber) ? null : valueAsNumber
}
