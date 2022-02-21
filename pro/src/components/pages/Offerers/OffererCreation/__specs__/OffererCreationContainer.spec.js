import { mapDispatchToProps, mergeProps } from '../OffererCreationContainer'

jest.mock('redux-saga-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
    createDataReducer: jest.fn(),
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
        showNotification: expect.any(Function),
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
          payload: {
            text: 'my message',
            type: 'success',
          },
          type: 'SHOW_NOTIFICATION',
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
        redirectAfterSubmit: expect.any(Function),
      })
    })
  })
})
