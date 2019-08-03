import moment from 'moment'

const getHumanizeRelativeDate = offerDate => {
  if (offerDate === null) return null

  const todayDate = new Date()
  const offerDateObject = new Date(offerDate)

  if (!(offerDateObject instanceof Date && !isNaN(offerDateObject)))
    throw new Error('Date invalide')

  const offerMoment = moment(offerDateObject)
  const todayMoment = moment(todayDate)
  const tomorrowMoment = moment(todayMoment)
  tomorrowMoment.add(1, 'day')

  if (offerMoment.isSame(todayMoment, 'day')) {
    return 'Aujourd’hui'
  }

  if (offerMoment.isSame(tomorrowMoment, 'day')) {
    return 'Demain'
  }

  return null
}

export default getHumanizeRelativeDate
