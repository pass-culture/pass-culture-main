import {
  getCoordinatesApiPathQueryString,
  getOfferIdAndMediationIdAndCoordinatesApiPathQueryString,
} from '../buildApiPathQueryString'

describe('src | components | pages | discovery | tests | helpers', () => {
  describe('getOfferIdAndMediationIdAndCoordinatesApiPathQueryString', () => {
    it('when current recommendation is not the same as query param recommendation should return correct query params', () => {
      // Given
      const coordinates = {}
      const currentRecommendation = {
        mediationId: 'ABC1',
        offerId: 'ABC2',
      }
      const match = {
        params: {
          mediationId: 'ABC3',
          offerId: 'ABC2',
        },
      }

      const expected = 'offerId=ABC2&mediationId=ABC3'

      // When
      const result = getOfferIdAndMediationIdAndCoordinatesApiPathQueryString(
        match,
        currentRecommendation,
        coordinates
      )

      // Then
      expect(result).toStrictEqual(expected)
    })

    it('when current recommendation is the same as query param recommendation should return empty string', () => {
      // Given
      const coordinates = {}
      const currentRecommendation = {
        offerId: 'ABC2',
        mediationId: 'ABC1',
      }
      const match = {
        params: {
          mediationId: 'ABC1',
          offerId: 'ABC2',
        },
      }

      const expected = ''

      // When
      const result = getOfferIdAndMediationIdAndCoordinatesApiPathQueryString(
        match,
        currentRecommendation,
        coordinates
      )

      // Then
      expect(result).toStrictEqual(expected)
    })

    it('when coordinates are provided should return correct query params with latitude and longitude', () => {
      // Given
      const coordinates = {
        latitude: 2.746,
        longitude: 48.76,
      }
      const currentRecommendation = {}
      const match = {
        params: {
          mediationId: 'ABC1',
          offerId: 'ABC2',
        },
      }

      const expected = 'offerId=ABC2&mediationId=ABC1&longitude=48.76&latitude=2.746'

      // When
      const result = getOfferIdAndMediationIdAndCoordinatesApiPathQueryString(
        match,
        currentRecommendation,
        coordinates
      )

      // Then
      expect(result).toStrictEqual(expected)
    })

    it('when recommendation does not have mediation should return correct query params', () => {
      // Given
      const coordinates = {
        latitude: 2.746,
        longitude: 48.76,
      }
      const currentRecommendation = {}
      const match = {
        params: {
          offerId: 'ABC1',
        },
      }

      const expected = 'offerId=ABC1&longitude=48.76&latitude=2.746'

      // When
      const result = getOfferIdAndMediationIdAndCoordinatesApiPathQueryString(
        match,
        currentRecommendation,
        coordinates
      )

      // Then
      expect(result).toStrictEqual(expected)
    })
  })

  describe('getCoordinatesApiPathQueryString', () => {
    describe('when coordinates are given', () => {
      it('should return string with latitude and longitude in query params', () => {
        // Given
        const coordinates = {
          longitude: 2.746,
          latitude: 48.76,
        }

        const expected = 'longitude=2.746&latitude=48.76'

        // When
        const result = getCoordinatesApiPathQueryString(coordinates)

        // Then
        expect(result).toStrictEqual(expected)
      })

      describe('when no coordinates are given', () => {
        it('should return empty string', () => {
          // Given
          const coordinates = {}

          const expected = ''

          // When
          const result = getCoordinatesApiPathQueryString(coordinates)

          // Then
          expect(result).toStrictEqual(expected)
        })
      })

      describe('when only one coordonate is given', () => {
        it('should return empty string when only latitude given', () => {
          // Given
          const coordinates = { latitude: 48.931 }

          const expected = ''

          // When
          const result = getCoordinatesApiPathQueryString(coordinates)

          // Then
          expect(result).toStrictEqual(expected)
        })

        it('should return empty string when only longitude given', () => {
          // Given
          const coordinates = { longitude: 1.831 }

          const expected = ''

          // When
          const result = getCoordinatesApiPathQueryString(coordinates)

          // Then
          expect(result).toStrictEqual(expected)
        })
      })
    })
  })
})
