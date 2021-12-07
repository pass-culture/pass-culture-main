export const parseDuration = (duration: string): number | undefined => {
  if (!duration) {
    return undefined
  }

  const [hours, minutes] = duration
    .split(':')
    .map(numberString => parseInt(numberString))

  return hours * 60 + minutes
}
