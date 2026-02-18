export const formatNumberLabel = (value: string | number): string | number => {
  if (typeof value === 'number') {
    return new Intl.NumberFormat('fr-FR', {
      useGrouping: true,
    }).format(value)
  }
  return value
}
