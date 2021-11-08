export const translateMinutesToHours = (durationInMinutes: number | null): string => {
  if (durationInMinutes === null || durationInMinutes === undefined) {
    return ''
  }
  const hours = Math.floor(durationInMinutes / 60)
  const minutes = (durationInMinutes % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
