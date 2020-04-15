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

// Cayenne              UTC          Paris                St Denis
//    | ---------------- | ----------- | --------------------|
//   9:00 ------------ 12:00 ------- 14:00 --------------- 16:00

export const getTimezone = departementCode => {
  switch (departementCode) {
    case '973':
      return 'America/Cayenne'
    case '974':
      return 'Indian/Reunion'
    default:
      return 'Europe/Paris'
  }
}
