import { buildArrayOf } from '../functions'

describe('buildTwoBlocsTile', () => {
  it('should return an array containing an array with cover', () => {
    // Given
    const cover = 'www.link-to-my-image.com'
    const hits = []

    // When
    const result = buildArrayOf({ cover, hits })

    // Then
    expect(result).toStrictEqual([[cover]])
  })

  it('should return an array containing an array with one hit', () => {
    // Given
    const hit = {
      offer: {
        dates: [],
        id: 'AE',
        isDuo: false,
        isEvent: false,
        name: 'Avengers - Age of Ultron',
        priceMin: 1,
        priceMax: 1,
        thumbUrl: 'my-thumb',
      },
      venue: {
        departementCode: '54',
        name: 'Librairie Kléber',
      },
    }
    const hits = [hit]

    // When
    const result = buildArrayOf({ hits })

    // Then
    expect(result).toStrictEqual([[hit]])
  })

  it('should return an array containing an array with two hits', () => {
    // Given
    const hit1 = {
      offer: {
        name: 'Avengers - Age of Ultron',
      },
    }
    const hit2 = {
      offer: {
        name: 'X-men Returns',
      },
    }
    const hits = [hit1, hit2]

    // When
    const result = buildArrayOf({ hits })

    // Then
    expect(result).toStrictEqual([[hit1, hit2]])
  })

  it('should return an array containing an array with three hits', () => {
    // Given
    const hit1 = {
      offer: {
        name: 'Avengers - Age of Ultron',
      },
    }
    const hit2 = {
      offer: {
        name: 'X-men Returns',
      },
    }
    const hit3 = {
      offer: {
        name: 'Hulk',
      },
    }
    const hits = [hit1, hit2, hit3]

    // When
    const result = buildArrayOf({ hits })

    // Then
    expect(result).toStrictEqual([[hit1, hit2], [hit3]])
  })

  it('should return an array containing an array with three hits and another with a cover', () => {
    // Given
    const hit1 = {
      offer: {
        name: 'Avengers - Age of Ultron',
      },
    }
    const hit2 = {
      offer: {
        name: 'X-men Returns',
      },
    }
    const hit3 = {
      offer: {
        name: 'Hulk',
      },
    }
    const cover = 'www.link-to-my-image.com'
    const hits = [hit1, hit2, hit3]

    // When
    const result = buildArrayOf({ hits, cover })

    // Then
    expect(result).toStrictEqual([[cover], [hit1, hit2], [hit3]])
  })
})
