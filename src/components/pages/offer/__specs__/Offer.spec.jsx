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
      isHomepageDisabled: true,
      match: {
        path: '/offre/details/ME/FA',
      },
    }
  })

  it('should display a close icon to /decouverte, details and footer for a given offer', () => {
    // given
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
    const closeIcon = wrapper.find(CloseLink)
    expect(closeIcon).toHaveLength(1)
    expect(closeIcon.prop('closeTo')).toBe('/decouverte')
  })

  it('should render a close icon to homepage url when homepage feature is enabled', () => {
    props.isHomepageDisabled = false
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
    const closeIcon = wrapper.find(CloseLink)
    expect(closeIcon.prop('closeTo')).toBe('/accueil')
  })
})
