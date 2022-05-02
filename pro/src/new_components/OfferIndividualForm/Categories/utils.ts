export const buildSelectOptions = <T>(
  getIdField: (item: T) => string | number,
  getValueField: (item: T) => string,
  data: T[]
) => {
  return data
    .map((item: T) => ({
      value: getIdField(item).toString(),
      label: getValueField(item),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}