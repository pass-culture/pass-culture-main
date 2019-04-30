import set from 'lodash.set'
import { getLinkDestination, getPriceValue, mapStateToProps, } from '../BookThisLinkContainer'

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

describe('src | components | verso | verso-controls | booking | BookThisLinkContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with an url and an array of prices', () => {
      // given
      const mockedUrl = `${offerId}/${mediationId}/`
      const mockedSearchQuery = '?search_query=parameter'
      const mockedRouter = {
        location: { search: mockedSearchQuery },
        match: {
          params: { mediationId, offerId },
          url: mockedUrl,
        },
      }
      const expected = {
        linkDestination: `${offerId}/${mediationId}/booking${mockedSearchQuery}`,
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
    it('should add booking to current url without query to open booking card', () => {
      // given
      const url = '/decouverte/offer_id/mediation_id/'
      const expected = '/decouverte/offer_id/mediation_id/booking'

      // when
      const result = getLinkDestination(url)

      // then
      expect(result).toStrictEqual(expected)
    })

    it('should add booking to current url with query to open booking card', () => {
      // given
      const url = '/decouverte/offer_id/mediation_id'
      const search = '?a_var=1'
      const expected = '/decouverte/offer_id/mediation_id/booking?a_var=1'

      // when
      const result = getLinkDestination(url, search)

      // then
      expect(result).toStrictEqual(expected)
    })

    it('should throw an error when argument is missing', () => {
      // given
      const url = null

      // when
      const result = () => getLinkDestination(url)

      expect(result).toThrow(Error)
    })

    it('should throw an error when argument type is not valid', () => {
      // given
      const url = { debug: 'this is an object not a string url' }

      // when
      const result = () => getLinkDestination(url)

      // then
      expect(result).toThrow(Error)
    })
  })
})
