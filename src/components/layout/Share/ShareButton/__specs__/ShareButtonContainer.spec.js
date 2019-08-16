import { shallow } from 'enzyme'
import configureStore from 'redux-mock-store'
import React from 'react'
import { Provider } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButtonContainer, { mapStateToProps } from '../ShareButtonContainer'
import { getShareURL } from '../../../../../helpers'

jest.mock('with-react-redux-login')
jest.mock('../../../../../helpers')

const middlewares = []
const mockStore = configureStore(middlewares)

const dispatchMock = jest.fn()

describe('src | components | share | ShareButtonContainer', () => {
  describe('snapshot', () => {
    it('should match the snapshot', () => {
      // given
      const initialState = {
        options: {},
        user: {
          email: 'fake@email.fr',
        },
        visible: true,
      }
      const store = mockStore(initialState)
      const props = {
        dispatch: dispatchMock,
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <ShareButtonContainer {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('mapStateToProps', () => {
    describe('when mapping offerName', () => {
      it('should get offerName from current offer', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId,
            },
          }
        }
        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation]
          }
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.offerName).toBe(offer.name)
      })
    })

    describe('when mapping text', () => {
      it('should build text from offerName', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId,
            },
          }
        }
        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation]
          }
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.text).toBe(
          "Retrouvez Marx et Compagnie sur le pass Culture"
        )
      })
    })

    describe('when mapping url', () => {
      describe('when user is logged in', () => {
        it('should getShareURL with location and user', () => {
          // given
          const offerId = 'B4'
          const offer = {
            id: offerId,
            name: 'Marx et Compagnie',
          }
          const recommendation = {
            id: 'PA',
            mediationId: 'CA',
            offerId,
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'CA',
                offerId,
              },
            }
          }
          const state = {
            data: {
              bookings: [],
              favorites: [],
              mediations: [],
              offers: [offer],
              recommendations: [recommendation]
            }
          }

          // when
          selectCurrentUser.mockReturnValue({ id: 'myId' })
          getShareURL.mockReturnValue('http://fake_shared_url')

          // then
          expect(mapStateToProps(state, ownProps).url).toBe('http://fake_shared_url')
        })
      })
    })

    describe('when mapping share data', () => {
      it('should explode all attributes from share', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          }
        }

        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation]
          },
          share: {
            options: false,
            visible: true,
          },
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.options).toBe(false)
        expect(result.visible).toBe(true)
      })
    })
  })
})
