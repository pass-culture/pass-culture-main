import { mapDispatchToProps } from '../OffererContainer'

describe('src | components | pages | Offerer | OffererContainer', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('mapDispatchToProps', () => {
    it('should return an object of functions', () => {
      // when
      const functions = mapDispatchToProps(dispatch)

      // then
      expect(functions).toStrictEqual({
        getOfferer: expect.any(Function),
        getUserOfferers: expect.any(Function),
        showNotification: expect.any(Function)
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
                stateKey: 'venues'
              }
            }
          },
          type: 'REQUEST_DATA_GET_/OFFERERS/AB'
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
            method: 'GET'
          },
          type: 'REQUEST_DATA_GET_/USEROFFERERS/AB'
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
            type: 'success'
          },
          type: 'SHOW_NOTIFICATION'
        })
      })
    })
  })
})
