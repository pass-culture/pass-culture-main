import { format, utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz'

export const formatLocalTimeDateString = (
  dateIsoString,
  departementCode,
  dateFormat = 'EEEE dd/MM/yyyy à HH:mm'
) => {
  const zonedDate = getLocalDepartementDateTimeFromUtc(dateIsoString, departementCode)
  return format(zonedDate, dateFormat, { timeZone: getDepartmentTimezone(departementCode) })
}

export const getLocalDepartementDateTimeFromUtc = (date, departementCode) =>
  utcToZonedTime(date, getDepartmentTimezone(departementCode))

export const getUtcDateTimeFromLocalDepartement = (zonedDate, departementCode) =>
  zonedTimeToUtc(zonedDate, getDepartmentTimezone(departementCode))

// Cayenne              UTC          Paris                St Denis
//    | ---------------- | ----------- | --------------------|
//   9:00 ------------ 12:00 ------- 14:00 --------------- 16:00

export const getDepartmentTimezone = departementCode => {
  // This mapping is also defined in the webapp and in the backend. Make
  // sure that all are synchronized.
  switch (departementCode) {
    case '971':
      return 'America/Guadeloupe'
    case '972':
      return 'America/Martinique'
    case '973':
      return 'America/Cayenne'
    case '974':
      return 'Indian/Reunion'
    case '975':
      return 'America/Miquelon'
    case '976':
      return 'Indian/Mayotte'
    case '977':
      return 'America/St_Barthelemy'
    case '978': // Saint-Martin
      return 'America/Guadeloupe'
    case '986':
      return 'Pacific/Wallis'
    case '987':
      // Polynésie actually spans multiple timezones. Use Papeete's timezone.
      return 'Pacific/Tahiti'
    case '988':
      return 'Pacific/Noumea'
    case '989': // Clipperton
      return 'Pacific/Pitcairn'
    default:
      return 'Europe/Paris'
  }
}
