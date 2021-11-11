import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { selectOfferByRouterMatch } from '../../../../../../../redux/selectors/data/offersSelectors'
import { getStubStore } from '../../../../../../../utils/stubStore'
import Price from '../../../../../Price/Price'
import BookingAction from '../BookingAction'
import BookingActionContainer from '../BookingActionContainer'

jest.mock('../../../../../../../redux/selectors/data/offersSelectors')

describe('components | BookingAction', () => {
  let props

  beforeEach(() => {
    props = {
      bookingUrl: 'http://booking-layout.com',
      history: createMemoryHistory(),
      moduleName: 'Nom du module',
      offerCannotBeBooked: false,
      priceRange: [10, 30],
    }
  })

  it('should render a clickable button when offer is bookable', () => {
    // given
    props.offerCannotBeBooked = false

    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    expect(wrapper.prop('className')).toBe('ticket-action')
    expect(wrapper.prop('disabled')).toBe(false)
    expect(wrapper.prop('onClick')).toStrictEqual(expect.any(Function))
    expect(wrapper.prop('type')).toBe('button')
  })

  it('should render a not clickable button when offer is not bookable', () => {
    // given
    props.offerCannotBeBooked = true

    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    expect(wrapper.prop('disabled')).toBe(true)
  })

  it('should render a price and label within link', () => {
    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    const price = wrapper.find(Price)
    expect(price).toHaveLength(1)
    expect(price.prop('className')).toBe('ticket-price')
    expect(price.prop('free')).toBe('Gratuit')
    expect(price.prop('value')).toStrictEqual([10, 30])
  })

  describe('when I click on button for booking', () => {
    it('should render the booking layout', () => {
      // given
      selectOfferByRouterMatch.mockReturnValueOnce({
        isBookable: true,
      })
      props.history.push('/decouverte?param=value', { moduleName: 'Nom du module' })
      const mockStore = getStubStore({
        data: (
          state = {
            bookings: [],
            mediations: [],
            offers: [],
            stocks: [],
          }
        ) => state,
      })

      const wrapper = mount(
        <Provider store={mockStore}>
          <Router history={props.history}>
            <BookingActionContainer />
          </Router>
        </Provider>
      )

      // when
      wrapper.find({ children: 'J’y vais !' }).simulate('click')

      // then
      expect(props.history.location.pathname).toStrictEqual('/decouverte/reservation')
      expect(props.history.location.search).toStrictEqual('?param=value')
      expect(props.history.location.state).toStrictEqual({ moduleName: 'Nom du module' })
    })
  })
})
