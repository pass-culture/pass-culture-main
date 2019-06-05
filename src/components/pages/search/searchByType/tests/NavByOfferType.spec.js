import React from 'react'
import { shallow } from 'enzyme'

import NavByOfferType from '../NavByOfferType'

describe('src | components | search | NavByOfferType', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        resetSearchReducer: jest.fn(),
        title: 'fake Title',
        typeSublabels: [],
        updateSearchQuery: jest.fn(),
      }

      // when
      const wrapper = shallow(<NavByOfferType {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('items renderer', () => {
    it('should render a list of items', () => {
      // given
      const typeSublabels = [
        'Sublabel 1',
        'Sublabel 2',
        'Sublabel 3',
        'Sublabel 4',
      ]
      const props = {
        resetSearchStore: jest.fn(),
        title: 'fake Title',
        typeSublabels,
        updateSearchQuery: jest.fn(),
      }
      const wrapper = shallow(<NavByOfferType {...props} />)

      // when
      const navitem = wrapper.find('.item')

      // then
      const len = typeSublabels.length
      expect(navitem.length).toEqual(len)
    })
  })

  describe('items clicked', () => {
    const typeSublabels = [
      'Sublabel 1',
      'Sublabel 2',
      'Sublabel 3',
      'Sublabel 4',
    ]
    it('should called resetSearchStore', () => {
      // given
      const resetSearchStoreMock = jest.fn()
      const props = {
        resetSearchStore: resetSearchStoreMock,
        title: 'fake Title',
        typeSublabels,
        updateSearchQuery: jest.fn(),
      }
      const wrapper = shallow(<NavByOfferType {...props} />)

      // when
      const navitem = wrapper.find('#button-nav-by-offer-type-sublabel-3')

      // then
      expect(navitem.length).toEqual(1)
      navitem.first().simulate('click')
      expect(resetSearchStoreMock).toHaveBeenCalled()
    })

    it('should called updateSearchQuery', () => {
      // given
      const updateSearchQueryMock = jest.fn()
      const props = {
        resetSearchStore: updateSearchQueryMock,
        title: 'fake Title',
        typeSublabels,
        updateSearchQuery: jest.fn(),
      }
      const wrapper = shallow(<NavByOfferType {...props} />)

      // when
      const navitem = wrapper.find('#button-nav-by-offer-type-sublabel-3')

      // then
      expect(navitem.length).toEqual(1)
      navitem.first().simulate('click')
      expect(updateSearchQueryMock).toHaveBeenCalled()
    })
  })
})
