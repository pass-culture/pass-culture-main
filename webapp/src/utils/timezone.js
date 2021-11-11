import moment from 'moment-timezone'

export const getTimezone = departementCode => {
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
