import React from 'react'
import { shallow } from 'enzyme'
import RawEventOccurrencesAndStocksManager, {
  getAddUrl,
} from '../RawEventOccurrencesAndStocksManager'

const mockedStock = {
  available: 10,
  bookingLimitDatetime: '2019-03-06T23:00:00Z',
  bookingRecapSent: null,
  dateModified: '2019-03-06T15:51:39.253527Z',
  dateModifiedAtLastProvider: '2019-03-06T15:51:39.253504Z',
  eventOccurrenceId: null,
  groupSize: 1,
  id: 'ARMQ',
  idAtProviders: null,
  isSoftDeleted: false,
  lastProviderId: null,
  modelName: 'Stock',
  offerId: 'AUSQ',
  price: 17,
}

describe.skip('src | components | pages | Offer | RawEventOccurrencesAndStocksManager', () => {
  // need to mock .focus()
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        location: {
          pathname: '/offres/AWHA',
          search: '?gestion',
          hash: '',
          state: undefined,
          key: '4c2v7m',
        },
        isEditing: false,
        stocks: [mockedStock],
      }

      // when
      const wrapper = shallow(
        <RawEventOccurrencesAndStocksManager {...initialProps} />
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('When isEditing a stock', () => {
      // given
      const initialProps = {
        location: {
          pathname: '/offres/AWHA',
          search: '?gestion',
          hash: '',
          state: undefined,
          key: '4c2v7m',
        },
        isEditing: 'MU',
        stocks: [mockedStock],
      }

      // when
      const wrapper = shallow(
        <RawEventOccurrencesAndStocksManager {...initialProps} />
      )

      // then
    })
    describe('When isNew', () => {
      it('should >>> ', () => {})
    })
    describe('When isStockOnly', () => {
      it('should >>> ', () => {})
    })
    describe('When Math.max > 12', () => {
      it('should >>> ', () => {})
    })
    describe('When provider', () => {
      it('should >>> ', () => {})
    })
    describe('When !isStockOnly', () => {
      it('should >>> ', () => {})
    })
  })

  describe('functions', () => {
    describe('componentDidMount', () => {
      // https://github.com/airbnb/enzyme/issues/393
      // https://stackoverflow.com/questions/48166739/jest-mock-document-activeelement?rq=1
    })
    describe('getAddUrl', () => {
      it('should return an event add URL', () => {
        // given
        const isEditing = false
        const isStockOnly = false
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = []
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual('/offres/42?gestion&date=nouvelle')
      })

      it('should return a thing add URL', () => {
        // given
        const isEditing = false
        const isStockOnly = true
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = []
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual('/offres/42?gestion&stock=nouveau')
      })

      it('should return the default URL', () => {
        // given
        const isEditing = true
        const isStockOnly = false
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = []
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual(defaultUrl)
      })

      it('should return the default URL', () => {
        // given
        const isEditing = true
        const isStockOnly = true
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = []
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual(defaultUrl)
      })

      it('should return a thing edition URL (do not allow multuple thing stocks)', () => {
        // given
        const isEditing = false
        const isStockOnly = true
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = [{ id: 'FE' }]
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual('/offres/42?gestion&stock=FE')
      })

      it('should return an event add URL (allow multiple event stocks)', () => {
        // given
        const isEditing = false
        const isStockOnly = false
        const offerId = 42
        const defaultUrl = `/offres/${offerId}`
        const stocks = [{ id: 'FE' }]
        // when
        const url = getAddUrl(
          isEditing,
          isStockOnly,
          offerId,
          stocks,
          defaultUrl
        )
        // then
        expect(url).toBeDefined()
        expect(url).toEqual('/offres/42?gestion&date=nouvelle')
      })
    })
  })
})
