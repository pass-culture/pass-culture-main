import { mapDispatchToProps, mapStateToProps, mergeProps } from '../OffererContainer'

describe('src | components | pages | Offerer | OffererContainer', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          offerers: [
            {
              id: 'AGH',
            },
          ],
          userOfferers: [
            {
              id: 'AEKQ',
              modelName: 'UserOfferer',
              offererId: 'AGH',
              rights: 'admin',
              userId: 'TY56er',
            },
          ],
          venues: [{}],
        },
        form: {
          offerer: {
            name: 'Fake Name',
          },
        },
      }

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
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        adminUserOfferer: {
          id: 'AEKQ',
          modelName: 'UserOfferer',
          offererId: 'AGH',
          rights: 'admin',
          userId: 'TY56er',
        },
        offerer: {
          id: 'AGH',
        },
        offererId: 'AGH',
        offererName: 'Fake Name',
        venues: [],
      })
    })
  })

  describe('mapDispatchToProps', () => {
    it('should return an object of functions', () => {
      // when
      const functions = mapDispatchToProps(dispatch)

      // then
      expect(functions).toStrictEqual({
        getOfferer: expect.any(Function),
        getUserOfferers: expect.any(Function),
        showNotification: expect.any(Function),
      })
    })

    describe('getOfferer', () => {
      it('should get offerer using API with the right parameters', () => {
        // given
        const offererId = 'AB'
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()
        const functions = mapDispatchToProps(dispatch)
        const { getOfferer } = functions

        // when
        getOfferer(offererId, handleFail, handleSuccess)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers/AB',
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'GET',
            normalizer: {
              managedVenues: {
                normalizer: { offers: 'offers' },
                stateKey: 'venues',
              },
            },
          },
          type: 'REQUEST_DATA_GET_/OFFERERS/AB',
        })
      })
    })

    describe('getUserOfferers', () => {
      it('should get user offerers using API with the right parameters', () => {
        // given
        const offererId = 'AB'
        const functions = mapDispatchToProps(dispatch)
        const { getUserOfferers } = functions

        // when
        getUserOfferers(offererId)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/userOfferers/AB',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/USEROFFERERS/AB',
        })
      })
    })

    describe('showNotification', () => {
      it('should display a notification with the right parameters', () => {
        // given
        const message = 'my message'
        const type = 'success'
        const functions = mapDispatchToProps(dispatch)
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
        trackModifyOfferer: expect.any(Function),
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

    it('should map a tracking event for update an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackModifyOfferer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'modifyOfferer',
        name: 'RTgfd67',
      })
    })
  })
})
