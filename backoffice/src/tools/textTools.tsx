export const snakeCaseToTitleCase = (str: string) => {
  return str
    .split('_')
    .filter(x => x.length > 0)
    .map(x => x.charAt(0).toUpperCase() + x.slice(1))
    .join(' ')
}
