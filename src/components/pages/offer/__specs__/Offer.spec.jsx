import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from '../../../../utils/stubStore'
import Offer from '../Offer'

describe('offer', () => {
  let props
  let mockStore

  beforeEach(() => {
    props = {
      match: {
        path:
          '/offre/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?',
      },
    }
  })

  it('should have a close link to home page and details of a given offer', () => {
    // given
    mockStore = getStubStore({
      currentUser: (
        state = {
          id: 'Rt4R45ETEs',
          wallet_balance: 0,
        }
      ) => state,
      data: (
        state = {
          bookings: [],
          offers: [{ id: 'ME', name: 'Offer name example' }],
          stocks: [],
          favorites: [],
          features: [],
          mediations: [],
          recommendations: [],
          users: [],
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
        <MemoryRouter initialEntries={['/offre/details/ME/FA']}>
          <Offer {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const closeLink = wrapper.find('a[href="/"]')
    expect(closeLink).toHaveLength(1)
    const closeIcon = closeLink.find('img[alt="Fermer"]')
    expect(closeIcon).toHaveLength(1)
    const detailsTitle = wrapper.find({ children: 'Offer name example' }).closest('h1')
    expect(detailsTitle).toHaveLength(1)
  })
})
