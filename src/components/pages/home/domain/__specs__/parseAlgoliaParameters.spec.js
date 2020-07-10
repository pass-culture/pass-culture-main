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
})
