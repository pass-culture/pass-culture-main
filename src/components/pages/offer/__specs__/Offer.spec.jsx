import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import getMockStore from '../../../../utils/mockStore'
import DetailsContainer from '../../../layout/Details/DetailsContainer'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import Offer from '../Offer'

describe('offer', () => {
  let props

  beforeEach(() => {
    props = {
      getOfferById: jest.fn(),
      match: {
        path: '/offre/details/ME/FA',
      },
    }
  })

  it('should display a close link and details for a given offer', () => {
    // given
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
        <MemoryRouter initialEntries={['/offre/details/ME/FA']}>
          <Offer {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const closeLink = wrapper.find(CloseLink)
    const offerDetails = wrapper.find(DetailsContainer)
    expect(closeLink).toHaveLength(1)
    expect(offerDetails.prop('getOfferById')).toBe(props.getOfferById)
  })
})
