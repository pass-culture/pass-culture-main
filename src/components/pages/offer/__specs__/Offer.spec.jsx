import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import getMockStore from '../../../../utils/mockStore'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import Offer from '../Offer'

describe('offer', () => {
  let props
  let mockStore

  beforeEach(() => {
    props = {
      homepageIsDisabled: true,
      getOfferById: jest.fn().mockReturnValue({ id: 'ME' }),
      match: {
        path: '/offre/details/ME/FA',
      },
    }
  })

  it('should render a close link to homepage url when homepage feature is enabled', () => {
    props.homepageIsDisabled = false
    mockStore = getMockStore({
      currentUser: (
        state = {
          id: 'Rt4R45ETEs',
          wallet_balance: 0,
        },
      ) => state,
      data: (
        state = {
          bookings: [],
          favorites: [],
          features: [],
          mediations: [],
          offers: [],
          stocks: [],
          recommendations: [],
          users: [],
        },
      ) => state,
      geolocation: (
        state = {
          latitude: 1,
          longitude: 2,
        },
      ) => state,
    })

    // when
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter initialEntries={['/offre/details/ME/FA']}>
          <Offer {...props} />
        </MemoryRouter>
      </Provider>,
    )

    // then
    const closeLink = wrapper.find(CloseLink)
    expect(closeLink.prop('closeTo')).toBe('/accueil')
  })
})
