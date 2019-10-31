import { shallow } from 'enzyme'
import React from 'react'

import NavByOfferType from '../NavByOfferType'
import SearchPicture from '../../SearchPicture'

describe('src | components | search | searchByType | NavByOfferType', () => {
  let props

  beforeEach(() => {
    // given
    props = {
      categories: ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
      resetSearchStore: jest.fn(),
      title: 'Fake title',
      updateSearchQuery: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NavByOfferType {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render a list of categories by default', () => {
      // given
      const wrapper = shallow(<NavByOfferType {...props} />)

      // when
      const categories = wrapper.find('.item')

      // then
      expect(categories).toHaveLength(props.categories.length)
      categories.forEach(category => {
        expect(category.children().is(SearchPicture)).toBe(true)
      })
    })

    describe('i click on one category', () => {
      it('should reset the search value of the store', () => {
        // given
        const wrapper = shallow(<NavByOfferType {...props} />)
        const categories = wrapper.find('.item')

        // when
        categories.first().simulate('click')

        // then
        expect(props.resetSearchStore).toHaveBeenCalledWith()
      })

      it('should update the search parameter of the query', () => {
        // given
        const wrapper = shallow(<NavByOfferType {...props} />)
        const categories = wrapper.find('.item')

        // when
        categories.first().simulate('click')

        // then
        expect(props.updateSearchQuery).toHaveBeenCalledWith(props.categories[0])
      })
    })
  })
})
