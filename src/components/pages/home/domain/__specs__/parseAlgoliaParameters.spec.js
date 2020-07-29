import { parseAlgoliaParameters } from '../parseAlgoliaParameters'

describe('src | components | parseAlgoliaParameters', () => {
  it('should return default parameters when no parameters are provided', () => {
    // given
    const parameters = {}

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
    })
  })

  it('should return parsed algolia parameters with categories when provided', () => {
    // given
    const parameters = {
      categories: ['CINEMA', 'LECON', 'LIVRE'],
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: ['CINEMA', 'LECON', 'LIVRE'],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
    })
  })

  it('should return parsed algolia parameters with tags when provided', () => {
    // given
    const parameters = {
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte'],
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: ['offre du 14 juillet spéciale pass culture', 'offre de la pentecôte'],
    })
  })

  it('should return parsed algolia parameters with hitsPerPage when provided', () => {
    // given
    const parameters = {
      hitsPerPage: 5,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: 5,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
    })
  })

  it('should return parsed algolia parameters with isDuo when provided', () => {
    // given
    const parameters = {
      isDuo: true,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: true,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
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
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: true,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
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
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: true, isEvent: false, isThing: false },
      priceRange: [],
      tags: [],
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
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: true, isThing: false },
      priceRange: [],
      tags: [],
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
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: true },
      priceRange: [],
      tags: [],
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
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: true, isEvent: true, isThing: true },
      priceRange: [],
      tags: [],
    })
  })

  it('should return algolia parameters with a price range when minimum price is provided', () => {
    // given
    const parameters = {
      priceMin: 50,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [50, 500],
      tags: [],
    })
  })

  it('should return algolia parameters with a price range when maximum price is provided', () => {
    // given
    const parameters = {
      priceMax: 300,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [0, 300],
      tags: [],
    })
  })

  it('should return algolia parameters with a price range when minimum and maximum prices are provided', () => {
    // given
    const parameters = {
      priceMin: 50,
      priceMax: 300,
    }

    // when
    const result = parseAlgoliaParameters(parameters)

    // then
    expect(result).toStrictEqual({
      hitsPerPage: null,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: false, isThing: false },
      priceRange: [50, 300],
      tags: [],
    })
  })
})
