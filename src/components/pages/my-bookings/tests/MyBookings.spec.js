import { shallow } from 'enzyme'
import React from 'react'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyBookings from '../MyBookings'
import NavigationFooter from '../../../layout/NavigationFooter'
import NoBookings from '../NoBookings'
import PageHeader from '../../../layout/Header/PageHeader'

describe('src | components | pages | my-bookings | MyBookings', () => {
  let props

  beforeEach(() => {
    props = {
      getMyBookings: jest.fn(),
      myBookings: [
        {
          id: 1,
        },
      ],
      soonBookings: [
        {
          id: 2,
        },
      ],
    }
  })

  describe('handleFail()', () => {
    it('should handle fail', () => {
      // given
      const wrapper = shallow(<MyBookings {...props} />)

      // when
      wrapper.instance().handleFail()

      // then
      expect(wrapper.state('hasError')).toBe(true)
      expect(wrapper.state('isLoading')).toBe(true)
    })
  })

  describe('handleSuccess()', () => {
    it('should handle success', () => {
      // given
      const wrapper = shallow(<MyBookings {...props} />)

      // when
      wrapper.instance().handleSuccess({}, { payload: { data: [] } })

      // then
      expect(wrapper.state('isEmpty')).toBe(true)
      expect(wrapper.state('isLoading')).toBe(false)
    })
  })

  describe('render()', () => {
    it('should render my soon or not bookings', () => {
      // when
      const wrapper = shallow(<MyBookings {...props} />)
      wrapper.setState({ isLoading: false })

      // then
      const pageHeader = wrapper.find(PageHeader)
      const ul = wrapper.find('ul')
      const navigationFooter = wrapper.find(NavigationFooter)
      expect(pageHeader).toHaveLength(1)
      expect(ul).toHaveLength(2)
      expect(navigationFooter).toHaveLength(1)
    })

    it('should render the Loader when there is something wrong with API', () => {
      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then
      const loaderContainer = wrapper.find(LoaderContainer)
      expect(loaderContainer).toHaveLength(1)
    })

    it('should not render my bookings when there are no bookings', () => {
      // given
      props.myBookings = []
      props.soonBookings = []

      // when
      const wrapper = shallow(<MyBookings {...props} />)
      wrapper.setState({
        isEmpty: true,
        isLoading: false,
      })

      // then
      const noBookings = wrapper.find(NoBookings)
      expect(noBookings).toHaveLength(1)
    })
  })
})
