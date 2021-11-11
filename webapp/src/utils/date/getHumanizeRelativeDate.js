import moment from 'moment-timezone'

const getHumanizeRelativeDate = (date, timezone) => {
  if (date === null) return null

  const todayDate = Date.now()
  const dateObject = new Date(date)

  if (!(dateObject instanceof Date && !isNaN(dateObject))) throw new Error('Date invalide')

  const offerMoment = moment(dateObject).tz(timezone)
  const todayMoment = moment(todayDate).tz(timezone)

  const tomorrowMoment = moment(todayMoment)
  tomorrowMoment.add(1, 'day')

  if (offerMoment.isSame(todayMoment, 'day') && offerMoment.isAfter(todayMoment)) {
    return 'Aujourd’hui'
  }

  if (offerMoment.isSame(tomorrowMoment, 'day')) {
    return 'Demain'
  }

  return null
}

export default getHumanizeRelativeDate
