export default <T extends { [key: string]: string }>(
  sourceArray: T[],
  sourceLabelKey: keyof T,
  sourceValueKey: keyof T,
  defaultOptionLabel: string
): SelectOptions => [
  { value: '', label: defaultOptionLabel },
  ...sourceArray.map(item => ({
    value: item[sourceValueKey],
    label: item[sourceLabelKey],
  })),
]
