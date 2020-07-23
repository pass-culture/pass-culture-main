import { parseAlgoliaParameters } from '../parseAlgoliaParameters'

describe('src | components | parseAlgoliaParameters', () => {
  it('should return parsed algolia parameters with categories only', () => {
    // given
    const parameters = {
      aroundRadius: 10000,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: ['CINEMA', 'LECON', 'LIVRE'],
      endingDatetime: '2020-07-15T00:00+02:00',
      hitsPerPage: 5,
      isDigital: false,
      isDuo: true,
      isEvent: true,
      isGeolocated: true,
      isThing: false,
      newestOnly: true,
      priceMax: 10,
      priceMin: 1,
      title: 'Mes paramètres Algolia'
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerCategories: ['CINEMA', 'LECON', 'LIVRE']
    })
  })

  it('should return empty algolia parameters when categories is empty', () => {
    // given
    const parameters = {
      aroundRadius: 10000,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: [],
      endingDatetime: '2020-07-15T00:00+02:00',
      hitsPerPage: 5,
      isDigital: false,
      isDuo: true,
      isEvent: true,
      isGeolocated: true,
      isThing: false,
      newestOnly: true,
      priceMax: 10,
      priceMin: 1,
      title: 'Mes paramètres Algolia'
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({})
  })

  it('should return parsed algolia parameters with tags only', () => {
    // given
    const parameters = {
      aroundRadius: 10000,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: [],
      endingDatetime: '2020-07-15T00:00+02:00',
      hitsPerPage: 5,
      isDigital: false,
      isDuo: true,
      isEvent: true,
      isGeolocated: true,
      isThing: false,
      newestOnly: true,
      priceMax: 10,
      priceMin: 1,
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte'],
      title: 'Mes paramètres Algolia'
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte']
    })
  })

  it('should return empty algolia parameters when tags are empty', () => {
    // given
    const parameters = {
      aroundRadius: 10000,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: [],
      endingDatetime: '2020-07-15T00:00+02:00',
      hitsPerPage: 5,
      isDigital: false,
      isDuo: true,
      isEvent: true,
      isGeolocated: true,
      isThing: false,
      newestOnly: true,
      priceMax: 10,
      priceMin: 1,
      tags: [],
      title: 'Mes paramètres Algolia'
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({})
  })
})
