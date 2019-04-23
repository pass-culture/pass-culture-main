import set from 'lodash.set'
import {
  getLinkDestination,
  getPriceValue,
  mapStateToProps,
} from '../BookThisButtonContainer'

const uniqId = 'BBB'
const offerId = 'AAA'
const mediationId = '123'
const stocks = [
  { available: 1, price: 0 },
  { available: 1, price: 30 },
  { available: 1, price: 12 },
]
const geolocation = { latitude: 1, longitude: 1 }
const mockedState = { geolocation }
set(mockedState, 'data', {
  recommendations: [
    {
      mediationId,
      offer: { stocks },
      offerId,
      uniqId,
    },
  ],
})

describe('src | components | verso | verso-buttons | BookThisButtonContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with an url and an array of prices', () => {
      // given
      const mockedUrl = `/decouverte/${offerId}/${mediationId}/`
      const mockedSearchQuery = '?search_query=parameter'
      const mockedRouter = {
        location: { search: mockedSearchQuery },
        match: {
          params: { mediationId, offerId },
          url: mockedUrl,
        },
      }
      const expected = {
        destinationPathname: `/decouverte/${offerId}/${mediationId}/booking`,
        destinationSearch: mockedSearchQuery,
        priceValue: [0, 30, 12],
      }

      // when
      const result = mapStateToProps(mockedState, mockedRouter)

      // then
      expect(result).toStrictEqual(expected)
    })
  })

  describe('getPriceValue', () => {
    it('should throw an error when no arguments', () => {
      // when
      const result = () => getPriceValue()

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when no params are empty', () => {
      // given
      const params = {}

      // when
      const result = () => getPriceValue(undefined, params)

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when state is empty', () => {
      // given
      const state = {}

      // when
      const result = () => getPriceValue(state, undefined)

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when state is empty and params is not an object', () => {
      // given
      const state = {}
      const params = 'this is not an object type'

      // when
      const result = () => getPriceValue(state, params)

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when state is not an object and params is given', () => {
      // given
      const state = 'this is not an object type'
      const params = {}

      // when
      const result = () => getPriceValue(state, params)

      // then
      expect(result).toThrow(Error)
    })

    it('should return an array of prices', () => {
      // given
      const params = { mediationId, offerId }
      const expected = [0, 30, 12]

      // when
      const result = getPriceValue(mockedState, params)

      // then
      expect(result).toStrictEqual(expected)
    })
  })

  describe('getLinkDestination', () => {
    it('should throw an error when match object is not an object', () => {
      // given
      const match = 'not an object'

      // when
      const result = () => getLinkDestination(match)

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when match does not contains params prop', () => {
      // given
      const match = {}

      // when
      const result = () => getLinkDestination(match)

      // then
      expect(result).toThrow(Error)
    })

    it('should throw an error when match.params does not contains offerId prop', () => {
      // given
      const match = { noOfferId: 'string' }

      // when
      const result = () => getLinkDestination(match)

      // then
      expect(result).toThrow(Error)
    })

    it('should contains decouverte keyword in destination pathname', () => {
      // given
      const params = { mediationId: 'BBBBB', offerId: 'AAAAA' }
      const expectedWithSlashes = '/decouverte/'

      // when
      const result = getLinkDestination({ params })

      // then
      expect(result).toContain(expectedWithSlashes)
    })

    it('should contains booking keyword in destination pathname', () => {
      // given
      const params = { mediationId: 'BBBBB', offerId: 'AAAAA' }
      const expectedWithSlashes = '/booking'

      // when
      const result = getLinkDestination({ params })

      // then
      expect(result).toContain(expectedWithSlashes)
    })

    it('should match results without mediationId', () => {
      // given
      const params = { offerId: 'AAAA' }
      const expectedWithSlashes = '/decouverte/AAAA/booking'

      // when
      const result = getLinkDestination({ params })

      // then
      expect(result).toStrictEqual(expectedWithSlashes)
    })

    it('should match results with mediationId', () => {
      // given
      const params = { mediationId: 'BBBB', offerId: 'AAAA' }
      const expectedWithSlashes = '/decouverte/AAAA/BBBB/booking'

      // when
      const result = getLinkDestination({ params })

      // then
      expect(result).toStrictEqual(expectedWithSlashes)
    })
  })
})
