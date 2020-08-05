import { buildPairedTiles, buildTiles } from '../buildTiles'

describe('src | buildTiles', () => {
  describe('buildPairedTiles', () => {
    it('should return an array containing an array with cover', () => {
      // Given
      const cover = 'www.link-to-my-image.com'
      const hits = []

      // When
      const result = buildPairedTiles({ cover, hits })

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
      const result = buildPairedTiles({ hits })

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
      const result = buildPairedTiles({ hits })

      // Then
      expect(result).toStrictEqual([[hit1, hit2]])
    })

    it('should return an array containing an array with two hits and another with one hit', () => {
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
      const result = buildPairedTiles({ hits })

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
      const result = buildPairedTiles({ hits, cover })

      // Then
      expect(result).toStrictEqual([[cover], [hit1, hit2], [hit3]])
    })

    describe('when see more tile is available', () => {
      it('should return an array containing an array with one hit and a true value', () => {
        // Given
        const hit1 = {
          offer: {
            name: 'Avengers - Age of Ultron',
          },
        }
        const nbHits = 2
        const hits = [hit1]

        // When
        const result = buildPairedTiles({ hits, nbHits })

        // Then
        expect(result).toStrictEqual([[hit1, true]])
      })

      it('should return an array containing an array with two hits and another array with a true value', () => {
        // Given
        const hit1 = {
          offer: {
            name: 'Avengers - Age of Ultron',
          },
        }
        const hit2 = {
          offer: {
            name: 'Matrix',
          },
        }
        const nbHits = 3
        const hits = [hit1, hit2]

        // When
        const result = buildPairedTiles({ hits, nbHits })

        // Then
        expect(result).toStrictEqual([[hit1, hit2], [true]])
      })

      it('should return an array containing an array with two hits and another array with one hit and a true value', () => {
        // Given
        const hit1 = {
          offer: {
            name: 'Avengers - Age of Ultron',
          },
        }
        const hit2 = {
          offer: {
            name: 'Matrix',
          },
        }
        const hit3 = {
          offer: {
            name: 'John Wick',
          },
        }
        const nbHits = 4
        const hits = [hit1, hit2, hit3]

        // When
        const result = buildPairedTiles({ hits, nbHits })

        // Then
        expect(result).toStrictEqual([[hit1, hit2], [hit3, true]])
      })
    })
  })

  describe('buildTiles', () => {
    it('should return an array containing a cover', () => {
      // Given
      const cover = 'www.link-to-my-image.com'
      const hits = []

      // When
      const result = buildTiles({ cover, hits })

      // Then
      expect(result).toStrictEqual([cover])
    })

    it('should return an array containing a cover and an offer', () => {
      // Given
      const cover = 'www.link-to-my-image.com'
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
      const result = buildTiles({ cover, hits })

      // Then
      expect(result).toStrictEqual([cover, hit])
    })

    it('should return an array containing a cover,an offer, a boolean true value', () => {
      // Given
      const cover = 'www.link-to-my-image.com'
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
      const nbHits = 5
      const hits = [hit]

      // When
      const result = buildTiles({ cover, hits, nbHits })

      // Then
      expect(result).toStrictEqual([cover, hit, true])
    })
  })
})
