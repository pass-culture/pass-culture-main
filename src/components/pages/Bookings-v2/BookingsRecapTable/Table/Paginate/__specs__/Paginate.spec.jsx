import { shallow } from 'enzyme'
import React from 'react'
import Paginate from '../Paginate'
import Icon from '../../../../../../layout/Icon'

describe('components | Paginate', () => {
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
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const previousPageButton = wrapper.find('button').find(Icon)
      expect(previousPageButton).toHaveLength(1)
      expect(previousPageButton.prop('svg')).toStrictEqual('ico-left-arrow')
    })

    it('should not display previous button when user cannot go back to previous page', () => {
      // given
      props.canPreviousPage = false

      // when
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const previousPageButton = wrapper.find('button').find(Icon)
      expect(previousPageButton).toHaveLength(0)
    })

    it('should display current page position', () => {
      // given
      props.currentPage = 1
      props.nbPages = 2

      // when
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const currentPage = wrapper.find({ children: 'Page 1/2' })
      expect(currentPage).toHaveLength(1)
    })

    it('should display next button when user can go to next page', () => {
      // given
      props.canNextPage = true

      // when
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const nextPageButton = wrapper.find('button').find(Icon)
      expect(nextPageButton).toHaveLength(1)
      expect(nextPageButton.prop('svg')).toStrictEqual('ico-right-arrow')
    })

    it('should not display next button when user cannot go to next page', () => {
      // given
      props.canNextPage = false

      // when
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const nextPageButton = wrapper.find('button').find(Icon)
      expect(nextPageButton).toHaveLength(0)
    })

    it('should display both previous & next buttons when user can go to previous or next page', () => {
      // given
      props.canNextPage = true
      props.canPreviousPage = true

      // when
      const wrapper = shallow(<Paginate {...props} />)

      // then
      const buttons = wrapper.find('button')
      expect(buttons).toHaveLength(2)

      const previousButton = buttons.at(0).find(Icon)
      expect(previousButton.prop('svg')).toStrictEqual('ico-left-arrow')

      const nextButton = buttons.at(1).find(Icon)
      expect(nextButton.prop('svg')).toStrictEqual('ico-right-arrow')
    })
  })

  describe('when clicking on buttons', () => {
    it('should go back to previous page when click on previous button', () => {
      // given
      props.canPreviousPage = true
      const wrapper = shallow(<Paginate {...props} />)
      const previousButton = wrapper.find('button')

      // when
      previousButton.simulate('click')

      // then
      expect(props.previousPage).toHaveBeenCalledTimes(1)
    })

    it('should go to next page when click on next button', () => {
      // given
      props.canNextPage = true
      const wrapper = shallow(<Paginate {...props} />)
      const nextButton = wrapper.find('button')

      // when
      nextButton.simulate('click')

      // then
      expect(props.nextPage).toHaveBeenCalledTimes(1)
    })
  })
})
