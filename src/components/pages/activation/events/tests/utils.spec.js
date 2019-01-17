// jest --env=jsdom ./src/components/pages/activation/events/tests/utils --watch
import {
  filterActivationOffers,
  mapActivationOffersToSelectOptions,
  orderObjectsByLabel,
  parseActivationOffers,
  groupOffersByCityCode,
} from '../utils'

import validOffers from './data/valid-offers.json'
import notValidOffers from './data/not-valid-offers.json'
import expectedGroupedOffers from './data/expected-grouped-offers.json'

describe('components | pages | activation | events | utils', () => {
  describe('filterActivationOffers', () => {
    it('filters activation offers with minimal properties', () => {
      // given
      const value = [...validOffers, ...notValidOffers]
      // when
      const result = filterActivationOffers(value)
      // then
      const expected = [...validOffers]
      expect(result).toStrictEqual(expected)
    })
  })
  describe('mapActivationOffersToSelectOptions', () => {
    it('transforms offers to usable options in selectbox component', () => {
      // given
      const value = [...validOffers]
      const expected = [
        {
          city: 'ville 1',
          code: '01000',
          label: 'B - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
        {
          city: 'ville 1',
          code: '01000',
          label: 'C - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
        {
          city: 'ville 2',
          code: '02000',
          label: 'A - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
      ]
      // when
      const result = mapActivationOffersToSelectOptions(value)
      // then
      expect(result).toStrictEqual(expected)
    })
  })
  describe('orderObjectsByLabel', () => {
    it('it expect something', () => {
      // given
      let value = [...validOffers]
      value = filterActivationOffers(value)
      value = mapActivationOffersToSelectOptions(value)
      // when
      const result = orderObjectsByLabel(value)
      // then
      expect(result[0].label).toStrictEqual('A - nom lieu')
      expect(result[1].label).toStrictEqual('B - nom lieu')
      expect(result[2].label).toStrictEqual('C - nom lieu')
    })
  })
  describe('parseActivationOffers', () => {
    it('it expect something', () => {
      // given
      const value = [...validOffers, ...notValidOffers]
      // when
      const result = parseActivationOffers(value)
      // then
      const expected = [
        {
          city: 'ville 2',
          code: '02000',
          label: 'A - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
        {
          city: 'ville 1',
          code: '01000',
          label: 'B - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
        {
          city: 'ville 1',
          code: '01000',
          label: 'C - nom lieu',
          url: '/decouverte/1234/5678?to=verso',
          value: 1234,
        },
      ]
      expect(result).toStrictEqual(expected)
    })
  })
  describe('groupOffersByCityCode', () => {
    it('it expect something', () => {
      // given
      const value = [...validOffers, ...notValidOffers]
      // when
      let result = parseActivationOffers(value)
      result = groupOffersByCityCode(result)
      // then
      const expected = [...expectedGroupedOffers]
      expect(result).toStrictEqual(expected)
    })
  })
})
