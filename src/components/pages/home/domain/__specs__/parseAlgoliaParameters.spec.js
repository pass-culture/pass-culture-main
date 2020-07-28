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

  it('should return algolia parameters with newestOnly when provided', () => {
    // given
    const parameters = {
      newestOnly: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerIsNew: true,
    })
  })

  it('should return algolia parameters with isDigital when provided', () => {
    // given
    const parameters = {
      isDigital: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerTypes: {
        isDigital: true,
        isEvent: false,
        isThing: false,
      },
    })
  })

  it('should return algolia parameters with isEvent when provided', () => {
    // given
    const parameters = {
      isEvent: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerTypes: {
        isDigital: false,
        isEvent: true,
        isThing: false,
      },
    })
  })

  it('should return algolia parameters with isThing when provided', () => {
    // given
    const parameters = {
      isThing: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerTypes: {
        isDigital: false,
        isEvent: false,
        isThing: true,
      },
    })
  })

  it('should return algolia parameters with all offer types when provided', () => {
    // given
    const parameters = {
      isDigital: true,
      isEvent: true,
      isThing: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      offerTypes: {
        isDigital: true,
        isEvent: true,
        isThing: true,
      },
    })
  })

})
