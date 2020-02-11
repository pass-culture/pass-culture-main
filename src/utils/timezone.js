import moment from 'moment-timezone'

export const formatLocalTimeDateString = (
  date,
  departementCode,
  dateFormat = 'dddd DD/MM/YYYY à HH:mm'
) => {
  const tz = getTimezone(departementCode)
  return moment(date)
    .tz(tz)
    .format(dateFormat)
}

export const getTimezone = departementCode => {
  switch (departementCode) {
    case '97':
      return 'America/Cayenne'
    case '973':
      return 'America/Cayenne'
    default:
      return 'Europe/Paris'
  }
}
