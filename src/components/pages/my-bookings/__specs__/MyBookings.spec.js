import { shallow } from 'enzyme'
import React from 'react'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyBookingContainer from '../MyBooking/MyBookingContainer'
import MyBookings from '../MyBookings'
import NavigationFooter from '../../../layout/NavigationFooter'
import NoItems from '../../../layout/NoItems/NoItems'
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

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<MyBookings {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleFail()', () => {
    it('should set hasError and isLoading to true in component state', () => {
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
    it('should set isLoading to false in component state', () => {
      // given
      const wrapper = shallow(<MyBookings {...props} />)

      // when
      wrapper.instance().handleSuccess({}, { payload: { data: [] } })

      // then
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

    describe('when there is something wrong with API', () => {
      it('should render the Loader', () => {
        // when
        const wrapper = shallow(<MyBookings {...props} />)

        // then
        const loaderContainer = wrapper.find(LoaderContainer)
        expect(loaderContainer).toHaveLength(1)
      })
    })

    describe('when there are no bookings', () => {
      it('should not render my bookings', () => {
        // given
        props.myBookings = []
        props.soonBookings = []

        // when
        const wrapper = shallow(<MyBookings {...props} />)
        wrapper.setState({
          isLoading: false,
        })

        // then
        const noItems = wrapper.find(NoItems)
        expect(noItems).toHaveLength(1)
        const myBookingContainer = wrapper.find(MyBookingContainer)
        expect(myBookingContainer).toHaveLength(0)
      })
    })
  })
})
