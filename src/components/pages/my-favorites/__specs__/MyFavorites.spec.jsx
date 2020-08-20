import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import getMockStore from '../../../../utils/mockStore'
import MyFavoriteDetailsContainer from '../MyFavoriteDetails/MyFavoriteDetailsContainer'
import MyFavorites from '../MyFavorites'
import MyFavoritesListContainer from '../MyFavoritesList/MyFavoritesListContainer'

describe('my favorites', () => {
  let mockStore
  let props

  beforeEach(() => {
    mockStore = getMockStore({
      currentUser: (
        state = {
          wallet_balance: 0,
        }
      ) => state,
      data: (
        state = {
          bookings: [],
          favorites: [],
          features: [],
          mediations: [],
          offers: [],
          recommendations: [],
          stocks: [],
          users: [
            {
              wallet_balance: '',
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
    props = {
      match: {
        path: '/favoris',
      },
    }
  })

  it('should display my favorites list', () => {
    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={['/favoris']}>
        <Provider store={mockStore}>
          <MyFavorites {...props} />
        </Provider>
      </MemoryRouter>
    )

    // then
    const myFavoritesListContainer = wrapper.find(MyFavoritesListContainer)
    expect(myFavoritesListContainer).toHaveLength(1)
  })

  describe('when clicking on an offer', () => {
    it('should display my favorites list and an offer', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/favoris/details/O1/M1']}>
          <Provider store={mockStore}>
            <MyFavorites {...props} />
          </Provider>
        </MemoryRouter>
      )

      // then
      const myFavoritesListContainer = wrapper.find(MyFavoritesListContainer)
      expect(myFavoritesListContainer).toHaveLength(1)
      const myFavoriteDetailsContainer = wrapper.find(MyFavoriteDetailsContainer)
      expect(myFavoriteDetailsContainer).toHaveLength(1)
    })
  })
})
