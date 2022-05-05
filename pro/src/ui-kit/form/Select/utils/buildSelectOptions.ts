export default <T extends { [key: string]: unknown }>(
  sourceArray: T[],
  sourceLabelKey: keyof T,
  sourceValueKey: keyof T,
  defaultOptionLabel: string
): SelectOptions => {
  const availableOptions = sourceArray.map(item => ({
    value: item[sourceValueKey] as string,
    label: item[sourceLabelKey] as string,
  }))

  return availableOptions.length !== 1
    ? [{ value: '', label: defaultOptionLabel }, ...availableOptions]
    : availableOptions
}
