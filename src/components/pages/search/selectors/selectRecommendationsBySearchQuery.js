import uniqBy from 'lodash.uniqby'
import moment from 'moment'
import { parse, stringify } from 'query-string'
import { createSelector } from 'reselect'

const PAGE_REGEXP = new RegExp(/&?page=\d+&?/)

const getRecommendationSearch = (search, types) => {
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
    const eventTypes = types.filter(type => type.type === 'Event')
    const thingTypes = types.filter(type => type.type === 'Thing')
    const matchingEventTypes = eventTypes.filter(eventType =>
      searchParams.categories.includes(eventType.sublabel)
    )
    const matchingThingTypes = thingTypes.filter(thingType =>
      searchParams.categories.includes(thingType.sublabel)
    )
    const matchingTypes = [...matchingEventTypes, ...matchingThingTypes]
    recommendationSearch['type_values'] = `[${matchingTypes
      .map(type => `'${type.value}'`)
      .join(', ')}]`
  }

  if (searchParams.date) {
    const dateContent = searchParams.jours
      .split(',')
      .map(joursInterval => {
        const joursIntervalContent = joursInterval
          .split('-')
          .map(jour => {
            const dateChunks = moment(searchParams.date)
              .add(jour, 'days')
              .toISOString()
              .split('T')
            const yymmdd = dateChunks[0]
              .split('-')
              .map(d => parseInt(d))
              .join(', ')
            const hhmmssmilliChunks = dateChunks[1].split('.')
            const hhmmss = hhmmssmilliChunks[0]
              .split(':')
              .map(d => parseInt(d))
              .join(', ')
            const milli =
              hhmmssmilliChunks[1]
                .split('.')
                .slice(-1)[0]
                .replace('Z', '') + '000'
            return `datetime.datetime(${yymmdd}, ${hhmmss}, ${milli}, tzinfo=tzlocal())`
          })
          .join(', ')
        return `[${joursIntervalContent}]`
      })
      .join(', ')
    recommendationSearch['days_intervals'] = `[${dateContent}]`
  }

  return decodeURI(stringify(recommendationSearch))
    .replace(/%2C /g, ', ')
    .replace(/%3D/g, '=')
}

const selectRecommendationsBySearchQuery = createSelector(
  state => state.data.recommendations,
  state => state.data.types,
  (state, location) => location.search.replace(PAGE_REGEXP, ''),
  (recommendations, types, searchWithoutPage) => {
    const searchQuery = getRecommendationSearch(searchWithoutPage, types)
    let filteredRecommendations = recommendations.filter(recommendation => {
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
