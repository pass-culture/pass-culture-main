import { DEFAULT_RECAP_VALUE } from '../constants'

export const formatDuration = (durationMinutes?: number | null) => {
  if (!durationMinutes) return DEFAULT_RECAP_VALUE

  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  if (hours === 0) {
    return `${minutes}min`
  }

  return `${hours}h${minutes > 0 ? `${minutes}min` : ''}`
}
