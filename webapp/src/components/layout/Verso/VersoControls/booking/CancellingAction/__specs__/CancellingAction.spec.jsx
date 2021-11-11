import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import moment from 'moment/moment'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router'

import { getStubStore } from '../../../../../../../utils/stubStore'
import CancellingAction from '../CancellingAction'
import CancellingActionContainer from '../CancellingActionContainer'

jest.mock('../../../../../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual(
    '../../../../../../../utils/fetch-normalize-data/reducers/data/actionCreators'
  )

  return {
    requestData: _requestData,
  }
})

describe('src | components | layout | Verso | VersoControls | booking | CancellingAction | CancellingAction', () => {
  let props

  beforeEach(() => {
    props = {
      booking: {
        id: 'AAA',
      },
      cancellingUrl: '/reservation/annulation',
      history: {
        push: jest.fn(),
      },
      location: {
        pathname: '',
        search: '',
      },
      match: { params: {} },
      offer: {},
      offerCanBeCancelled: true,
      openCancelPopin: jest.fn(),
      price: 20,
    }
  })

  describe('when event offer date is past', () => {
    it('should display disabled cancel button', () => {
      // given
      props.offerCanBeCancelled = false

      // when
      const wrapper = shallow(<CancellingAction {...props} />)

      // then
      const button = wrapper.find('button')
      expect(button.props().disabled).toBe(true)
    })
  })

  describe('when I click on button for cancelling', () => {
    it('should change the pathname', () => {
      // given
      const now = moment()
      const oneDayAfterNow = now.add(1, 'days').format()

      const mockHistory = createMemoryHistory()
      mockHistory.push('/reservations/details/b1?param=value')
      const mockStore = getStubStore({
        data: (
          state = {
            bookings: [
              {
                id: 'b1',
                stockId: 's1',
              },
            ],
            mediations: [],
            offers: [
              {
                id: 'o1',
              },
            ],
            stocks: [
              {
                id: 's1',
                offerId: 'o1',
                price: 20,
                beginningDatetime: oneDayAfterNow,
              },
            ],
          }
        ) => state,
      })
      const wrapper = mount(
        <Provider store={mockStore}>
          <Router history={mockHistory}>
            <Route path="/reservations/:details(details|transition)?/:bookingId?/:booking(reservation)?/:cancellation(annulation)?/:confirmation(confirmation)?">
              <CancellingActionContainer />
            </Route>
          </Router>
        </Provider>
      )

      // when
      wrapper.find({ children: 'Annuler' }).simulate('click')

      // then
      expect(`${mockHistory.location.pathname}${mockHistory.location.search}`).toBe(
        '/reservations/details/b1/reservation/annulation?param=value'
      )
    })
  })
})
