import { shallow } from 'enzyme'
import React from 'react'

import Icon from 'components/layout/Icon'

import TablePagination from '../TablePagination'

describe('components | TablePagination', () => {
  let props

  beforeEach(() => {
    props = {
      canNextPage: false,
      canPreviousPage: false,
      currentPage: 1,
      previousPage: jest.fn(),
      nbPages: 2,
      nextPage: jest.fn(),
    }
  })

  describe('render', () => {
    it('should display previous button when user can go back to previous page', () => {
      // given
      props.canPreviousPage = true

      // when
      const wrapper = shallow(<TablePagination {...props} />)

      // then
      const buttons = wrapper.find('button').find(Icon)
      const previousButton = buttons.at(0)
      expect(previousButton.prop('svg')).toBe('ico-left-arrow')
      expect(previousButton.prop('disabled')).toBeUndefined()
    })

    it('should display current page position', () => {
      // given
      props.currentPage = 1
      props.nbPages = 2

      // when
      const wrapper = shallow(<TablePagination {...props} />)

      // then
      const currentPage = wrapper.find({ children: 'Page 1/2' })
      expect(currentPage).toHaveLength(1)
    })

    it('should display next button when user can go to next page', () => {
      // given
      props.canNextPage = true

      // when
      const wrapper = shallow(<TablePagination {...props} />)

      // then
      const buttons = wrapper.find('button').find(Icon)
      const nextButton = buttons.at(1)
      expect(nextButton).toHaveLength(1)
      expect(nextButton.prop('svg')).toBe('ico-right-arrow')
    })
  })

  describe('when clicking on buttons', () => {
    it('should go back to previous page when click on previous button', () => {
      // given
      props.canPreviousPage = true
      const wrapper = shallow(<TablePagination {...props} />)
      const buttons = wrapper.find('button')
      const previousButton = buttons.at(0)

      // when
      previousButton.simulate('click')

      // then
      expect(props.previousPage).toHaveBeenCalledTimes(1)
    })

    it('should go to next page when click on next button', () => {
      // given
      props.canNextPage = true
      const wrapper = shallow(<TablePagination {...props} />)
      const buttons = wrapper.find('button')
      const nextButton = buttons.at(1)

      // when
      nextButton.simulate('click')

      // then
      expect(props.nextPage).toHaveBeenCalledTimes(1)
    })
  })
})
