import { getTimezone } from '../timezone'

const rawDate = (date, delta = 0) => new Date(date).setDate(date.getDate() + delta)

export const humanizeRelativeDate = offerDate => {
  if (offerDate === null) return null

  const todayWithoutHour = new Date().toISOString().substring(0, 10)
  const offerDateWithoutHour = offerDate.substring(0, 10)
  const today = new Date(todayWithoutHour)
  const dateObject = new Date(offerDateWithoutHour)

  if (!(dateObject instanceof Date && !isNaN(dateObject))) throw new Error('Date invalide')

  const rawOfferDate = rawDate(dateObject)
  const rawToday = rawDate(today)
  const rawTomorrow = rawDate(today, 1)

  if (rawOfferDate === rawToday) {
    return 'Aujourd’hui'
  }

  if (rawOfferDate === rawTomorrow) {
    return 'Demain'
  }

  return null
}

const formatDate = (date, timeZone) => {
  const options = {
    timeZone,
    weekday: 'long',
  }

  return `${date.toLocaleDateString('fr-FR', options)} ${date.toLocaleDateString()}`
}

export const formatRecommendationDates = (departementCode, dateRange = []) => {
  if (dateRange.length === 0) return 'permanent'

  const timeZone = getTimezone(departementCode)
  const fromDate = new Date(dateRange[0])
  const toDate = new Date(dateRange[1])
  const fromFormated = formatDate(fromDate, timeZone)
  const toFormated = formatDate(toDate, timeZone)

  return `du ${fromFormated} au ${toFormated}`
}
