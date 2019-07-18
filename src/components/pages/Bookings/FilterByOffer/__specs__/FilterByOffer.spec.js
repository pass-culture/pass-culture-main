import React from 'react'
import { shallow } from 'enzyme/build'

import FilterByDateContainer from '../../FilterByDate/FilterByDateContainer'
import { FilterByOffer } from '../FilterByOffer'

describe('src | components | pages | FilterByOffer', () => {
  describe('the date section', () => {
    it('should be hidden when `all offer is selected', () => {
      // given
      const props = {
        isFilterByDigitalVenues: false,
        loadOffers: jest.fn(),
        offersOptions: [],
        selectBookingsForOffers: jest.fn(),
        showDateSection: false,
      }

      // when
      const wrapper = shallow(<FilterByOffer {...props} />)

      // then
      const filterByDateContainer = wrapper.find(FilterByDateContainer)
      expect(filterByDateContainer).toHaveLength(0)
    })

    it('should display offer section when a specific offer is selected', () => {
      // given
      const props = {
        isFilterByDigitalVenues: false,
        loadOffers: jest.fn(),
        offersOptions: [],
        selectBookingsForOffers: jest.fn(),
        showDateSection: true,
      }

      // when
      const wrapper = shallow(<FilterByOffer {...props} />)

      // then
      const filterByDateContainer = wrapper.find(FilterByDateContainer)
      expect(filterByDateContainer).toHaveLength(1)
    })
  })
})
