import { createMemoryHistory } from 'history'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router'
import { getCurrentUserUUID } from 'with-react-redux-login'

import AbsoluteFooterContainer from '../../../layout/AbsoluteFooter/AbsoluteFooterContainer'
import DetailsContainer from '../../../layout/Details/DetailsContainer'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import OfferContainer from '../OfferContainer'
import getMockStore from '../../../../utils/mockStore'

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
    it('should display header, details and footer for a given offer', () => {
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
                currentUserUUID: getCurrentUserUUID(),
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
      const header = wrapper.find(HeaderContainer)
      const offerDetails = wrapper.find(DetailsContainer)
      const footer = wrapper.find(AbsoluteFooterContainer)
      expect(header).toHaveLength(1)
      expect(offerDetails).toHaveLength(1)
      expect(footer).toHaveLength(2)
    })
  })
})
