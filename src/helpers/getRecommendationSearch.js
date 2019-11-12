import moment from 'moment'
import { parse, stringify } from 'query-string'

import { DEFAULT_MAX_DISTANCE } from '../components/pages/search/helpers'

const getMatchingEventTypes = (types, categories) => {
  const eventTypes = types.filter(type => type.type === 'Event')
  return eventTypes.filter(eventType => categories.includes(eventType.sublabel))
}

const getMatchingThingTypes = (types, categories) => {
  const thingTypes = types.filter(type => type.type === 'Thing')
  return thingTypes.filter(thingType => categories.includes(thingType.sublabel))
}

const getMatchingTypes = (categories, types) => {
  const matchingEventTypes = getMatchingEventTypes(types, categories)
  const matchingThingTypes = getMatchingThingTypes(types, categories)
  return [...matchingEventTypes, ...matchingThingTypes]
}

const getStringifiedTypeValues = types => `[${types.map(type => `'${type.value}'`).join(', ')}]`

const getDateAndTime = (startDate, day) =>
  moment(startDate)
    .add(day, 'days')
    .toISOString()
    .split('T')

const getStringifiedDate = date =>
  date
    .split('-')
    .map(d => parseInt(d))
    .join(', ')

const getStringifiedTime = time => {
  const hhmmssmilliChunks = time.split('.')
  const hhmmss = hhmmssmilliChunks[0]
    .split(':')
    .map(d => parseInt(d))
    .join(', ')
  const milli =
    hhmmssmilliChunks[1]
      .split('.')
      .slice(-1)[0]
      .replace('Z', '') + '000'
  return `${hhmmss}, ${milli}`
}

const getDatetimeString = (startDate, day) => {
  const [date, time] = getDateAndTime(startDate, day)
  const dateString = getStringifiedDate(date)
  const timeString = getStringifiedTime(time)
  return `datetime.datetime(${dateString}, ${timeString}, tzinfo=tzlocal())`
}

const getStringifiedDaysIntervals = (startDate, daysString) =>
  `[${daysString
    .split(',')
    .map(daysInterval => {
      const daysIntervalContent = daysInterval
        .split('-')
        .map(day => getDatetimeString(startDate, day))
        .join(', ')
      return `[${daysIntervalContent}]`
    })
    .join(', ')}]`

const getStringifiedRecommendationSearch = recommendationSearch => {
  if (Object.keys(recommendationSearch).length === 0) {
    return ''
  }
  return decodeURI(stringify(recommendationSearch))
    .replace(/%2C /g, ', ')
    .replace(/%3D/g, '=')
}

export const getRecommendationSearch = (search, types) => {
  const searchParams = parse(search)
  const recommendationSearch = {}

  if (searchParams['mots-cles']) {
    recommendationSearch['keywords_string'] = searchParams['mots-cles']
  }

  if (searchParams.distance && searchParams.distance !== DEFAULT_MAX_DISTANCE) {
    recommendationSearch['max_distance'] = `${searchParams.distance}.0`
    recommendationSearch['latitude'] = searchParams.latitude
    recommendationSearch['longitude'] = searchParams.longitude
  }

  if (searchParams.categories) {
    const decodedCategoriesString = decodeURIComponent(searchParams.categories)
    const matchingTypes = getMatchingTypes(decodedCategoriesString, types)
    recommendationSearch['type_values'] = getStringifiedTypeValues(matchingTypes)
  }

  if (searchParams.date) {
    recommendationSearch['days_intervals'] = getStringifiedDaysIntervals(
      searchParams.date,
      searchParams.jours
    )
  }

  if (searchParams.page) {
    recommendationSearch['page'] = searchParams.page
  }

  return getStringifiedRecommendationSearch(recommendationSearch)
}
