import { minutesToHours } from 'date-fns'

export const parseMinutesToHours = (durationTime: number) => {
  if (durationTime === 0) return ''
  const hours = minutesToHours(durationTime).toString()
  const minutes = (durationTime % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
