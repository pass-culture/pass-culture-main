// jest --env=jsdom ./src/components/verso/verso-buttons/tests/BookThisButtonContainer --watch
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
    it('returns an object with an url and an array of prices', () => {
      const mockedUrl = `${offerId}/${mediationId}/`
      const mockedSearchQuery = '?search_query=parameter'
      const mockedRouter = {
        location: { search: mockedSearchQuery },
        match: {
          params: { mediationId, offerId },
          url: mockedUrl,
        },
      }
      const result = mapStateToProps(mockedState, mockedRouter)
      const expected = {
        linkDestination: `${offerId}/${mediationId}/booking${mockedSearchQuery}`,
        priceValue: [0, 30, 12],
      }
      expect(result).toStrictEqual(expected)
    })
  })
  describe('getPriceValue', () => {
    it('throws with missing or invalid arguments', () => {
      expect(() => getPriceValue()).toThrow()
      let params = {}
      expect(() => getPriceValue(undefined, params)).toThrow()
      let state = {}
      expect(() => getPriceValue(state, undefined)).toThrow()
      state = {}
      params = 'this is not an object type'
      expect(() => getPriceValue(state, params)).toThrow()
      state = 'this is not an object type'
      params = {}
      expect(() => getPriceValue(state, params)).toThrow()
    })
    it('returns an array of prices', () => {
      const params = { mediationId, offerId }
      const result = getPriceValue(mockedState, params)
      const expected = [0, 30, 12]
      expect(result).toStrictEqual(expected)
    })
  })
  describe('getLinkDestination', () => {
    it('add booking to current url without query to open booking card', () => {
      const url = '/decouverte/offer_id/mediation_id/'
      const expected = '/decouverte/offer_id/mediation_id/booking'
      const result = getLinkDestination(url)
      expect(result).toStrictEqual(expected)
    })
    it('add booking to current url with query to open booking card', () => {
      const url = '/decouverte/offer_id/mediation_id'
      const search = '?a_var=1'
      const expected = '/decouverte/offer_id/mediation_id/booking?a_var=1'
      const result = getLinkDestination(url, search)
      expect(result).toStrictEqual(expected)
    })
    it('throw with missing argument', () => {
      const url = null
      expect(() => getLinkDestination(url)).toThrow()
    })
    it('throw with wrong argument type', () => {
      const url = { debug: 'this is an object not a string url' }
      expect(() => getLinkDestination(url)).toThrow()
    })
  })
})
