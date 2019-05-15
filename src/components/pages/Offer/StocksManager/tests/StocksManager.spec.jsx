import { shallow } from 'enzyme'
import React from 'react'

import StocksManager from '../StocksManager'

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

describe('src | components | pages | Offer | StocksManager', () => {
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
        query: { context: () => ({}) },
        stocks: [mockedStock],
      }

      // when
      const wrapper = shallow(<StocksManager {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
