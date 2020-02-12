import React from 'react'
import { shallow } from 'enzyme'

import StocksManager from '../StocksManager'

describe('components | OfferEdition | StocksManager', () => {
  let props
  let query
  const stock = {
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

  beforeEach(() => {
    query = {
      changeToCreation: jest.fn(),
      context: () => ({}),
    }
    props = {
      dispatch: jest.fn(),
      isEvent: true,
      location: {
        pathname: '/offres/AWHA',
        search: '?gestion',
        hash: '',
        state: undefined,
        key: '4c2v7m',
      },
      query,
      shouldPreventCreationOfSecondStock: false,
      stocks: [stock],
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<StocksManager {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('onClickCreateStockItem()', () => {
    it('should update URL query param when click on add stock button', () => {
      // given
      const wrapper = shallow(<StocksManager {...props} />)
      const button = wrapper.find('#add-stock')

      // when
      button.simulate('click')

      // then
      expect(query.changeToCreation).toHaveBeenCalledWith(null, {
        key: 'stock',
      })
    })
  })

  describe('render()', () => {
    it('should return a error message', () => {
      // given
      props.query = { context: () => ({}) }
      const wrapper = shallow(<StocksManager {...props} />)
      wrapper.setState({
        errors: {
          global: ['Mon message d’erreur custom'],
        },
      })

      // when
      const errorMessage = wrapper.find('.is-danger').text()

      // then
      expect(errorMessage).toBe('global : Mon message d’erreur custom')
    })
  })
})
