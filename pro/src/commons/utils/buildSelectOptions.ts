import type { SelectOption } from '../custom_types/form'

export const buildSelectOptions = (
  rec: Record<string, string>
): SelectOption[] => {
  return Object.entries(rec).map(([value, label]) => ({
    label,
    value,
  }))
}
