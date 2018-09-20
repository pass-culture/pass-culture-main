import moment from 'moment'

export function formatLocalTimeDateString(date, departementCode) {
  const tz = getTimezone(departementCode)
  return moment(date)
    .tz(tz)
    .format('dddd DD/MM/YYYY à HH:mm')
}

export function getTimezone(departementCode) {
  switch (departementCode) {
    case '97':
      return 'America/Cayenne'
    case '973':
      return 'America/Cayenne'
    default:
      return 'Europe/Paris'
  }
}

export default getTimezone
