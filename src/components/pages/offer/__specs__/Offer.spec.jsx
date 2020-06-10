import { mount } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import getMockStore from '../../../../utils/mockStore'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import OfferContainer from '../OfferContainer'

jest.mock('../../../hocs/with-login/withRequiredLogin', () => WrappedComponent => props => (
  <WrappedComponent {...props} />
))

describe('offerContainer', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          details: 'details',
          offerId: 'o1',
        },
      },
    }
  })

  describe('when I am logged in', () => {
    it('should display a close link, details and footer for a given offer', () => {
      // given
      const mockHistory = createMemoryHistory()
      const mockStore = getMockStore({
        data: (
          state = {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [],
            stocks: [],
            recommendations: [],
            users: [
              {
                id: 'Rt4R45ETEs',
                wallet_balance: 0,
              },
            ],
          }
        ) => state,
        geolocation: (
          state = {
            latitude: 1,
            longitude: 2,
          }
        ) => state,
      })

      // when
      const wrapper = mount(
        <Provider store={mockStore}>
          <Router history={mockHistory}>
            <OfferContainer {...props} />
          </Router>
        </Provider>
      )

      // then
      const closeLink = wrapper.find(CloseLink)
      const offerDetails = wrapper.find(DetailsContainer)
      expect(closeLink).toHaveLength(1)
      expect(offerDetails).toHaveLength(1)
    })
  })
})
