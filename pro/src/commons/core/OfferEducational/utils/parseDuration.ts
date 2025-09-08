export const parseDuration = (duration: string): number | undefined => {
  if (!duration) {
    return undefined
  }

  const [hours, minutes] = duration
    .split(':')
    .map((numberString) => parseInt(numberString, 10))

  return hours * 60 + minutes
}
