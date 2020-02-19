import moment from 'moment'
import 'moment-timezone'

import { getTimezone } from '../timezone'
import { capitalize } from '../react-form-utils/functions'

const PASS_CULTURE_YEARS_VALIDITY = 2

const formatDate = (date, timeZone) => {
  const options = {
    timeZone,
  }

  return `${date.toLocaleDateString('fr-FR', options)}`
}

export const formatRecommendationDates = (departementCode, dateRange = []) => {
  if (dateRange.length === 0) return 'permanent'

  const timeZone = getTimezone(departementCode)
  const fromDate = new Date(dateRange[0])
  const toDate = new Date(dateRange[1])
  const fromFormated = formatDate(fromDate, timeZone)
  const toFormated = formatDate(toDate, timeZone)

  return `du ${fromFormated} au ${toFormated}`
}

export const computeEndValidityDate = date => {
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
  date.setFullYear(date.getFullYear() + PASS_CULTURE_YEARS_VALIDITY)

  return `${date.toLocaleDateString('fr-FR', options)}`
}

export const dateStringPlusTimeZone = (dateString, departementCode) => {
  return moment(dateString)
    .tz(getTimezone(departementCode))
    .format('YYYY-MM-DD HH:mm:ss')
}

export const humanizeDate = (date, timezone) =>
  capitalize(
    moment(date)
      .tz(timezone)
      .format('dddd DD/MM/YYYY à H:mm')
  )
