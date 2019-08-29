import uniqBy from 'lodash.uniqby'
import { parse, stringify } from 'query-string'
import { createSelector } from 'reselect'

const getRecommendationSearch = (search, types) => {
  const searchParams = parse(search)
  const recommendationSearch = {}
  console.log({searchParams, search, types})

  if (searchParams.keywords) {
    recommendationSearch['keywords_string'] = searchParams.keywords
  }

  if (searchParams.categories) {
    const eventTypes = types.filter(type => type.type === 'Event')
    const thingTypes = types.filter(type => type.type === 'Thing')
    const matchingEventTypes = eventTypes.filter(eventType =>
      searchParams.categories.includes(eventType.sublabel))
    console.log()
    const matchingThingTypes = thingTypes.filter(thingType => {
      console.log(thingType.value, thingType.sublabel)
      return searchParams.categories.includes(thingType.sublabel)
    })
    const matchingTypes = [...matchingEventTypes, ...matchingThingTypes]
    recommendationSearch['type_values'] = matchingTypes
      .map(type => `'${type.value}'`).join(', ')
  }

  if (searchParams.date) {
    recommendationSearch['days_intervals'] = searchParams.date
  }

  if (searchParams.distance) {
    recommendationSearch['max_distance'] = searchParams.distance
  }

  console.log({recommendationSearch})

  return stringify(recommendationSearch)
}

const selectRecommendationsBySearchQuery = createSelector(
  state => state.data.recommendations,
  state => state.data.types,
  (state, location) => location.search,
  (recommendations, types, search) => {
    const searchQuery = getRecommendationSearch(search, types)
    /*
      if 'categories' in request_args and request_args['categories']:
          type_sublabels = request_args['categories']
          search_params['type_values'] = get_event_or_thing_type_values_from_sublabels(
              type_sublabels)

      if 'date' in request_args and request_args['date']:
          date = dateutil.parser.parse(request_args['date'])
          search_params['days_intervals'] = [
              [date, date + timedelta(days=int(1))]]

      if 'days' in request_args and request_args['days']:
          date = dateutil.parser.parse(request_args['date'])
          days_intervals = request_args['days'].split(',')
          search_params['days_intervals'] = [
              [date + timedelta(days=int(day)) for day in days.split('-')]
              for days in days_intervals
          ]
    */

    if (recommendations[0]) {
      console.log({locationSearch: search})
      console.log({searchQuery})
      console.log({firstRecommendationSearch: recommendations[0].search})
    }

    let filteredRecommendations = recommendations.filter(
      recommendation => recommendation.search === searchQuery
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.productOrTutoIdentifier
    )

    return filteredRecommendations
  }
)

export default selectRecommendationsBySearchQuery
