import { setUniqIdOnRecommendation } from '../recommendation'

describe('utils recommendation', () => {
  describe('when recommendation is an event', () => {
    it('should return an object having an `uniqId` property begining with `event_`', () => {
      // Given
      const recommendation = {
        offer: {
          eventId: 42,
        },
      }

      // When
      const result = setUniqIdOnRecommendation(recommendation)

      // Then
      expect(result.uniqId).toEqual('event_42')
    })
  })

  describe('when recommendation is a thing', () => {
    it('should return an object having an `uniqId` property begining with `thing_`', () => {
      // Given
      const recommendation = {
        offer: {
          thingId: 1337,
        },
      }

      // When
      const result = setUniqIdOnRecommendation(recommendation)

      // Then
      expect(result.uniqId).toEqual('thing_1337')
    })
  })

  describe('when recommendation is a tuto', () => {
    it('should return an object having an `uniqId` property begining with `tuto_`', () => {
      // Given
      const recommendation = {
        mediation: {
          tutoIndex: 'test',
        },
      }

      // When
      const result = setUniqIdOnRecommendation(recommendation)

      // Then
      expect(result.uniqId).toEqual('tuto_test')
    })
  })
})
