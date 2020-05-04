import moment from 'moment-timezone'

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

export const getTimezoneFromOffer = offer => {
  const { venue } = offer
  const { departementCode } = venue
  return getTimezone(departementCode)
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
