import moment from 'moment-timezone'

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

export const setTimezoneOnBeginningDatetime = timezone => stocks =>
  stocks.map(stock => {
    let extend = {}
    if (stock.beginningDatetime) {
      const dateWithTimezone = moment(stock.beginningDatetime).tz(timezone)
      extend = { beginningDatetime: dateWithTimezone }
    }
    return Object.assign({}, stock, extend)
  })

export default getTimezone
