import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import getMockStore from '../../../../utils/mockStore'
import Booking from '../../../layout/Booking/Booking'
import MyFavorites from '../MyFavorites'

describe('my favorites', () => {
  let fakeMatomo
  let mockStore

  beforeEach(() => {
    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    mockStore = getMockStore({
      currentUser: (
        state = {
          wallet_balance: 0,
        }
      ) => state,
      data: (
        state = {
          bookings: [
            {
              stockId: 's1',
            },
          ],
          favorites: [],
          mediations: [],
          offers: [
            {
              id: 'o1',
              isEvent: true,
              product: {
                thumbUrl: '',
              },
            },
          ],
          recommendations: [],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
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
  })

  it('should display the title "Favoris"', () => {
    // given
    const props = {
      deleteFavorites: jest.fn(),
      loadMyFavorites: jest.fn(),
      match: {
        path: '/favoris',
      },
      myFavorites: [],
    }

    jest.spyOn(props, 'loadMyFavorites').mockImplementation((fail, success) => success())

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.match.path]}>
        <Provider store={mockStore}>
          <MyFavorites {...props} />
        </Provider>
      </MemoryRouter>
    )

    // then
    const title = wrapper.find('h1').find({ children: 'Favoris' })
    expect(title).toHaveLength(1)
  })

  describe('render()', () => {
    describe('when on details page I can initiate booking', () => {
      it('should open booking component with offerId and mediationId on url', () => {
        // given
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
          match: {
            path: '/favoris',
          },
          myFavorites: [
            {
              id: 1,
              offerId: 'AM3A',
              offer: {
                id: 'AM3A',
                name: 'name',
              },
              mediationId: 'B4',
              mediation: {
                id: 'B4',
                thumbUrl: 'thumbUrl',
              },
            },
          ],
        }

        // when
        const wrapper = mount(
          <MemoryRouter initialEntries={[`${props.match.path}/details/AM3A/B4/reservation`]}>
            <Provider store={mockStore}>
              <MyFavorites {...props} />
            </Provider>
          </MemoryRouter>
        )

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })

      it('should open booking component with no mediationId on url', () => {
        // given
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
          match: {
            path: '/favoris',
          },
          myFavorites: [
            {
              id: 1,
              offerId: 'AM3A',
              offer: {
                id: 'AM3A',
                name: 'name',
              },
            },
          ],
        }

        // when
        const wrapper = mount(
          <MemoryRouter initialEntries={[`${props.match.path}/details/AM3A/vide/reservation`]}>
            <Provider store={mockStore}>
              <MyFavorites {...props} />
            </Provider>
          </MemoryRouter>
        )

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })
    })
  })
})
