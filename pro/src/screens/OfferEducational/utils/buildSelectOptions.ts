export default <T extends { [key: string]: unknown }>(
  sourceArray: T[],
  sourceLabelKey: keyof T,
  sourceValueKey: keyof T,
  defaultOptionLabel: string
): SelectOptions => [
  { value: '', label: defaultOptionLabel },
  ...sourceArray.map(item => ({
    value: item[sourceValueKey] as string,
    label: item[sourceLabelKey] as string,
  })),
]
