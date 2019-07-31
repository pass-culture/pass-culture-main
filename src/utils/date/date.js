const rawDate = (date, delta = 0) => new Date(date).setDate(date.getDate() + delta)

export const humanizeRelativeDate = offerDate => {
  if (offerDate === null) return null

  const today = new Date()
  const dateObject = new Date(offerDate)

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
