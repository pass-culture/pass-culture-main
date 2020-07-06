import configureStore from 'redux-mock-store'
import { createMemoryHistory } from 'history'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import thunk from 'redux-thunk'

import Booking from '../../../layout/Booking/Booking'
import MyFavorites from '../MyFavorites'
import state from '../../../../mocks/state'

describe('my favorites', () => {
  let fakeMatomo

  beforeEach(() => {
    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
  })

  it('should display the title "Favoris"', () => {
    // given
    const buildStore = configureStore([thunk])
    const store = buildStore(state)
    const history = createMemoryHistory()
    const props = {
      deleteFavorites: jest.fn(),
      loadMyFavorites: jest.fn(),
      myFavorites: [],
    }

    history.push('/favoris')

    jest.spyOn(props, 'loadMyFavorites').mockImplementation((fail, success) => success())

    // when
    const wrapper = mount(
      <Router history={history}>
        <Provider store={store}>
          <MyFavorites {...props} />
        </Provider>
      </Router>
    )

    // then
    const title = wrapper.find('h1').find({ children: 'Favoris' })
    expect(title).toHaveLength(1)
  })

  describe('render()', () => {
    describe('when on details page I can initiate booking', () => {
      it('should open booking component with offerId and mediationId on url', () => {
        // given
        const buildStore = configureStore([thunk])
        const store = buildStore(state)
        const history = createMemoryHistory()
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
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
        history.push('/favoris/details/AM3A/B4/reservation')

        // when
        const wrapper = mount(
          <Router history={history}>
            <Provider store={store}>
              <MyFavorites {...props} />
            </Provider>
          </Router>
        )

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })

      it('should open booking component with no mediationId on url', () => {
        // given
        const buildStore = configureStore([thunk])
        const store = buildStore(state)
        const history = createMemoryHistory()
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
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
        history.push('/favoris/details/AM3A/vide/reservation')
        const wrapper = mount(
          <Router history={history}>
            <Provider store={store}>
              <MyFavorites {...props} />
            </Provider>
          </Router>
        )

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })
    })
  })
})
