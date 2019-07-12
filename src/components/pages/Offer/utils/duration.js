export const getDurationInHours = durationInMinutes => {
  if (!durationInMinutes || durationInMinutes === 0) return 'HH:MM'

  let hours = Math.floor(durationInMinutes / 60)
  let minutes = durationInMinutes % 60

  if (hours < 10) {
    hours = `0${hours}`
  }

  if (minutes < 10) {
    minutes = `0${minutes}`
  }

  return `${hours}:${minutes}`
}

export const getDurationInMinutes = durationInHours => {
  if (!durationInHours || durationInHours.length === 0) {
    return null
  }

  let hours = Number(durationInHours.slice(0, 2))
  let minutes = Number(durationInHours.slice(3))

  if (hours < 1) {
    return minutes
  }
  return hours * 60 + minutes
}
