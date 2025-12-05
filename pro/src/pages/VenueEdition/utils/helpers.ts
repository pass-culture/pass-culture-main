import { isPlainObject } from '@/commons/utils/isPlainObject'

export function diffObjects(
  current: Record<string, unknown>,
  base: Record<string, unknown>
): Record<string, unknown> {
  const diff: Record<string, unknown> = {}
  const keys = new Set([...Object.keys(current), ...Object.keys(base)])

  for (const key of keys) {
    const currentValue = current[key]
    const baseValue = base[key]

    if (areValuesEqual(currentValue, baseValue)) {
      continue
    }

    if (currentValue !== undefined) {
      diff[key] = currentValue
    }
  }

  return diff
}

function areValuesEqual(value: unknown, baseValue: unknown): boolean {
  if (value === baseValue) {
    return true
  }

  if (Array.isArray(value) && Array.isArray(baseValue)) {
    if (value.length !== baseValue.length) {
      return false
    }

    return value.every((item, index) => areValuesEqual(item, baseValue[index]))
  }

  if (isPlainObject(value) && isPlainObject(baseValue)) {
    const valueKeys = Object.keys(value)
    const baseKeys = Object.keys(baseValue)

    if (valueKeys.length !== baseKeys.length) {
      return false
    }

    return valueKeys.every((key) =>
      areValuesEqual(
        (value as Record<string, unknown>)[key],
        (baseValue as Record<string, unknown>)[key]
      )
    )
  }

  return false
}
