import uniqBy from 'lodash.uniqby'
import moment from 'moment'
import { parse, stringify } from 'query-string'
import { createSelector } from 'reselect'

const PAGE_REGEXP = new RegExp(/&?page=\d+&?/)

const getMatchingEventTypes = (types, categories) => {
  const eventTypes = types.filter(type => type.type === 'Event')
  return eventTypes.filter(eventType => categories.includes(eventType.sublabel))
}

const getMatchingThingTypes = (types, categories) => {
  const thingTypes = types.filter(type => type.type === 'Thing')
  return thingTypes.filter(thingType => categories.includes(thingType.sublabel))
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

const getDatetimeString = (startDate, jour) => {
  const [date, time] = getDateAndTime(startDate, jour)
  const dateString = getStringifiedDate(date)
  const timeString = getStringifiedTime(time)
  return `datetime.datetime(${dateString}, ${timeString}, tzinfo=tzlocal())`
}

const getStringifiedDaysIntervals = (startDate, daysString) =>
  `[${daysString
    .split(',')
    .map(joursInterval => {
      const joursIntervalContent = joursInterval
        .split('-')
        .map(jour => getDatetimeString(startDate, jour))
        .join(', ')
      return `[${joursIntervalContent}]`
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

  if (searchParams.distance) {
    recommendationSearch['max_distance'] = `${searchParams.distance}.0`
    recommendationSearch['latitude'] = searchParams.latitude
    recommendationSearch['longitude'] = searchParams.longitude
  }

  if (searchParams.categories) {
    const matchingEventTypes = getMatchingEventTypes(types, searchParams.categories)
    const matchingThingTypes = getMatchingThingTypes(types, searchParams.categories)
    const matchingTypes = [...matchingEventTypes, ...matchingThingTypes]
    recommendationSearch['type_values'] = getStringifiedTypeValues(matchingTypes)
  }

  if (searchParams.date) {
    recommendationSearch['days_intervals'] = getStringifiedDaysIntervals(
      searchParams.date,
      searchParams.jours
    )
  }

  return getStringifiedRecommendationSearch(recommendationSearch)
}

const selectRecommendationsBySearchQuery = createSelector(
  state => state.data.recommendations,
  state => state.data.types,
  (state, location) => location.search.replace(PAGE_REGEXP, ''),
  (recommendations, types, searchWithoutPage) => {
    const searchQuery = getRecommendationSearch(searchWithoutPage, types)

    let filteredRecommendations = recommendations.filter(recommendation => {
      if (recommendation.search === null) {
        return false
      }
      const searchRecommendationWithoutPage = recommendation.search.replace(PAGE_REGEXP, '')
      return searchRecommendationWithoutPage === searchQuery
    })

    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.productOrTutoIdentifier
    )

    return filteredRecommendations
  }
)

export default selectRecommendationsBySearchQuery
