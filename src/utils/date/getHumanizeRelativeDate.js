import moment from 'moment'

const getHumanizeRelativeDate = (offerDate, offerTimezone) => {
  if (offerDate === null) return null

  const todayDate = new Date(Date.now())
  const offerDateObject = new Date(offerDate)

  if (!(offerDateObject instanceof Date && !isNaN(offerDateObject)))
    throw new Error('Date invalide')

  const offerMoment = moment(offerDateObject).tz(offerTimezone)
  const todayMoment = moment(todayDate).tz(offerTimezone)

  const tomorrowMoment = moment(todayMoment)
  tomorrowMoment.add(1, 'day')

  if (offerMoment.isSame(todayMoment, 'day')) {
    if (offerMoment.isBefore(todayMoment)) {
      return null
    }
    return 'Aujourd’hui'
  }

  if (offerMoment.isSame(tomorrowMoment, 'day')) {
    return 'Demain'
  }

  return null
}

export default getHumanizeRelativeDate
