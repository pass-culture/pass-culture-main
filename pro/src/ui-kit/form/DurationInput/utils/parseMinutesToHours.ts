export const parseMinutesToHours = (durationTime: number) => {
  if (durationTime === 0) return ''
  const hours = Math.floor(durationTime / 60)
  const minutes = (durationTime % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
