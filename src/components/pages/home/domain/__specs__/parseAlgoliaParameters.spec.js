import { parseAlgoliaParameters } from '../parseAlgoliaParameters'

describe('src | components | parseAlgoliaParameters', () => {
  it('should return empty algolia parameters when no parameters', () => {
    // given
    const parameters = {}

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({})
  })

  it('should return parsed algolia parameters with categories only', () => {
    // given
    const parameters = {
      categories: ['CINEMA', 'LECON', 'LIVRE'],
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerCategories: ['CINEMA', 'LECON', 'LIVRE'],
    })
  })

  it('should return parsed algolia parameters with tags only', () => {
    // given
    const parameters = {
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte'],
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte'],
    })
  })

  it('should return parsed algolia parameters with hitsPerPage only', () => {
    // given
    const parameters = {
      hitsPerPage: 5,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: 5,
    })
  })

  it('should return parsed algolia parameters with isDuo only', () => {
    // given
    const parameters = {
      isDuo: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerIsDuo: true,
    })
  })
})
