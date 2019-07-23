import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import { ShareButtonContainer } from '../ShareButton/ShareButton'
import { mapStateToProps } from '../ShareButton/ShareButtonContainer'

import { selectCurrentRecommendation } from '../../../selectors/currentRecommendation/currentRecommendation'
import { selectCurrentUser } from 'with-react-redux-login'

import { getShareURL } from '../../../helpers'

jest.mock('../../../selectors/currentRecommendation/currentRecommendation')
jest.mock('with-react-redux-login')
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
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('mapStateToProps', () => {
    describe('when mapping offerName', () => {
      it('should get offerName from current recommendation', () => {
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const state = {
          data: {
            recommendations: [
              {
                id: 'PA',
                mediationId: 'CA',
                offerId: 'B4',
                offer: {
                  name: 'offerName',
                },
              },
            ],
          },
        }

        selectCurrentRecommendation.mockReturnValue(state.data.recommendations[0])
        selectCurrentUser.mockReturnValue({})

        expect(mapStateToProps(state, ownprops).offerName).toBe('offerName')
      })
    })

    describe('when mapping text', () => {
      it('should build text from recommendation offerName', () => {
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const state = {
          data: {
            recommendations: [
              {
                id: 'PA',
                mediationId: 'CA',
                offerId: 'B4',
                offer: {
                  name: 'offerName',
                },
              },
            ],
          },
        }

        selectCurrentRecommendation.mockReturnValue(state.data.recommendations[0])
        selectCurrentUser.mockReturnValue({})

        expect(mapStateToProps(state, ownprops).text).toBe(
          'Retrouvez offerName sur le pass Culture'
        )
      })
    })

    describe('when mapping url', () => {
      describe('when user is logged in', () => {
        it('should getShareURL with location and user', () => {
          const ownprops = {
            match: {
              params: {
                mediationId: 'CA',
                offerId: 'B4',
              },
            },
          }
          const state = {
            data: {
              recommendations: [
                {
                  id: 'PA',
                  mediationId: 'CA',
                  offerId: 'B4',
                  offer: {
                    name: 'offerName',
                  },
                },
              ],
            },
          }

          selectCurrentRecommendation.mockReturnValue(state.data.recommendations[0])
          selectCurrentUser.mockReturnValue({ id: 'myId' })
          getShareURL.mockReturnValue('http://fake_shared_url')

          expect(mapStateToProps(state, ownprops).url).toBe('http://fake_shared_url')
        })
      })
    })

    describe('when mapping share data', () => {
      it('should explode all attributes from share', () => {
        const ownprops = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const state = {
          data: {
            recommendations: [
              {
                id: 'PA',
                mediationId: 'CA',
                offerId: 'B4',
                offer: {
                  name: 'offerName',
                },
              },
            ],
          },
          share: {
            options: false,
            visible: true,
          },
        }

        selectCurrentRecommendation.mockReturnValue(state.data.recommendations[0])
        selectCurrentUser.mockReturnValue({})

        expect(mapStateToProps(state, ownprops).options).toBe(false)
        expect(mapStateToProps(state, ownprops).visible).toBe(true)
      })
    })
  })
})
