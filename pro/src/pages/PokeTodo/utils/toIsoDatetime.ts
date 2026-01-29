export function toIsoDatetime(
  datetimeLocalValue: string | null
): string | null {
  if (!datetimeLocalValue) {
    return null
  }

  if (datetimeLocalValue.endsWith('Z')) {
    return datetimeLocalValue
  }

  return `${datetimeLocalValue}:00Z`
}
