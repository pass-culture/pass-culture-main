import { mapDispatchToProps, mergeProps } from '../OffererCreationContainer'

jest.mock('redux-saga-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
  }
})

describe('src | components | pages | Offerer | OfferCreation | OffererCreationContainer', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('mapDispatchToProps', () => {
    it('should return an object of functions', () => {
      // given
      const ownProps = {
        currentUser: {
          id: 'TY56er',
        },
        match: {
          params: {
            offererId: 'AGH',
          },
        },
      }
      // when
      const functions = mapDispatchToProps(dispatch, ownProps)

      // then
      expect(functions).toStrictEqual({
        closeNotification: expect.any(Function),
        createNewOfferer: expect.any(Function),
        showNotification: expect.any(Function),
        redirectToOfferersList: expect.any(Function),
      })
    })

    describe('showNotification', () => {
      it('should display a notification with the right parameters', () => {
        // given
        const ownProps = {
          currentUser: {
            id: 'TY56er',
          },
          match: {
            params: {
              offererId: 'AGH',
            },
          },
        }
        const message = 'my message'
        const type = 'success'
        const functions = mapDispatchToProps(dispatch, ownProps)
        const { showNotification } = functions

        // when
        showNotification(message, type)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            text: 'my message',
            type: 'success',
          },
          type: 'SHOW_NOTIFICATION',
        })
      })
    })

    describe('closeNotification', () => {
      it('enable to close notification', () => {
        // when
        mapDispatchToProps(dispatch).closeNotification()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          type: 'CLOSE_NOTIFICATION',
        })
      })
    })

    describe('createNewOfferer', () => {
      it('should dispatch', () => {
        // Given
        const ownProps = {
          currentUser: {
            id: 'TY56er',
          },
          match: {
            params: {
              offererId: 'AGH',
            },
          },
        }
        const { createNewOfferer } = mapDispatchToProps(dispatch, ownProps)
        const payload = {
          key: 'value',
          siren: '123 456 789',
        }

        // When
        createNewOfferer(payload)

        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers',
            method: 'POST',
            body: {
              key: 'value',
              siren: '123456789',
            },
          },
          type: 'REQUEST_DATA_POST_/OFFERERS',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        getOfferer: () => {},
      }
      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        getOfferer: expect.any(Function),
        match: ownProps.match,
        trackCreateOfferer: expect.any(Function),
      })
    })

    it('should map a tracking event for create an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackCreateOfferer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'createOfferer',
        name: 'RTgfd67',
      })
    })
  })
})
