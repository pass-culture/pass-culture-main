const getDurationInHours = durationInMinutes => {
  if (!durationInMinutes) durationInMinutes = 0
  const d = new Date()
  d.setHours(0)
  d.setMinutes(durationInMinutes)
  let minutes = d.getMinutes()
  let hours = d.getHours()

  if (hours < 10) {
    hours = `0${hours}`
  }
  if (minutes < 10) {
    minutes = `0${minutes}`
  }

  return `${hours}:${minutes}`
}

export const getDurationInMinutes = durationInHours => {
  let hours = Number(durationInHours.slice(0, 2))
  let minutes = Number(durationInHours.slice(3))
  if (hours < 1) {
    return minutes
  }
  return hours * 60 + minutes
}

export default getDurationInHours
