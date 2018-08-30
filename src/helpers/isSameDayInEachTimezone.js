// We use format so that each date is converted to a day in its own timezone
export const isSameDayInEachTimezone = (a, b) =>
  a.format('YYYYMMDD') === b.format('YYYYMMDD')

export default isSameDayInEachTimezone
