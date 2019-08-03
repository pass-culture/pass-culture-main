import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import ShareButtonContainer, { mapStateToProps } from '../ShareButton/ShareButtonContainer'

import { selectCurrentRecommendation } from '../../../selectors/currentRecommendation/currentRecommendation'
import { selectCurrentUser } from 'with-react-redux-login'

import { getShareURL } from '../../../helpers'

jest.mock('with-react-redux-login')
jest.mock('../../../selectors/currentRecommendation/currentRecommendation')
jest.mock('../../../helpers')

const middlewares = []
const mockStore = configureStore(middlewares)

const dispatchMock = jest.fn()

describe('src | components | share | ShareButtonContainer', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
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
      it('should get offerName from current recommendation', () => {
        // given
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const currentRecommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId: 'B4',
          offer: {
            name: 'offerName',
          },
        }
        const state = {
          data: {
            recommendations: [currentRecommendation],
          },
        }

        // when
        selectCurrentRecommendation.mockReturnValue(currentRecommendation)
        selectCurrentUser.mockReturnValue({})

        // then
        expect(mapStateToProps(state, ownprops).offerName).toBe('offerName')
      })
    })

    describe('when mapping text', () => {
      it('should build text from recommendation offerName', () => {
        // given
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const currentRecommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId: 'B4',
          offer: {
            name: 'offerName',
          },
        }
        const state = {
          data: {
            recommendations: [currentRecommendation],
          },
        }

        // when
        selectCurrentRecommendation.mockReturnValue(currentRecommendation)
        selectCurrentUser.mockReturnValue({})

        // then
        expect(mapStateToProps(state, ownprops).text).toBe(
          'Retrouvez offerName sur le pass Culture'
        )
      })
    })

    describe('when mapping url', () => {
      describe('when user is logged in', () => {
        it('should getShareURL with location and user', () => {
          // given
          const ownprops = {
            match: {
              params: {
                mediationId: 'CA',
                offerId: 'B4',
              },
            },
          }
          const currentRecommendation = {
            id: 'PA',
            mediationId: 'CA',
            offerId: 'B4',
            offer: {
              name: 'offerName',
            },
          }
          const state = {
            data: {
              recommendations: [currentRecommendation],
            },
          }

          // when
          selectCurrentRecommendation.mockReturnValue(currentRecommendation)
          selectCurrentUser.mockReturnValue({ id: 'myId' })
          getShareURL.mockReturnValue('http://fake_shared_url')

          // then
          expect(mapStateToProps(state, ownprops).url).toBe('http://fake_shared_url')
        })
      })
    })

    describe('when mapping share data', () => {
      it('should explode all attributes from share', () => {
        // given
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const currentRecommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId: 'B4',
          offer: {
            name: 'offerName',
          },
        }
        const state = {
          data: {
            recommendations: [currentRecommendation],
          },
          share: {
            options: false,
            visible: true,
          },
        }

        // when
        selectCurrentRecommendation.mockReturnValue(currentRecommendation)
        selectCurrentUser.mockReturnValue({})

        // then
        expect(mapStateToProps(state, ownprops).options).toBe(false)
        expect(mapStateToProps(state, ownprops).visible).toBe(true)
      })
    })
  })
})
