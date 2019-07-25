import { mapDispatchToProps } from '../MediationContainer'

describe('src | components | pages | MediationContainer', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {}
  })

  describe('mapDispatchToProps', () => {
    it('should return an object containing five functions', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        getOffer: expect.any(Function),
        getMediation: expect.any(Function),
        showFailDataNotification: expect.any(Function),
        showSuccessDataNotification: expect.any(Function),
        createOrUpdateMediation: expect.any(Function),
      })
    })
  })

  describe('getOffer', () => {
    it('should retrieve offer with offerId', () => {
      // given
      const { getOffer } = mapDispatchToProps(dispatch, props)

      // when
      getOffer('OfferId')

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/offers/OfferId',
          method: 'GET',
          normalizer: {
            mediations: 'mediations',
            product: {
              normalizer: {
                offers: 'offers',
              },
              stateKey: 'products',
            },
            stocks: 'stocks',
            venue: {
              normalizer: {
                managingOfferer: 'offerers',
              },
              stateKey: 'venues',
            },
          },
        },
        type: 'REQUEST_DATA_GET_/OFFERS/OFFERID',
      })
    })
  })

  describe('getMediation', () => {
    it('should retrieve mediation with mediationId', () => {
      // given
      const { getMediation } = mapDispatchToProps(dispatch, props)

      // when
      getMediation('mediationId', jest.fn(), jest.fn())

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/mediations/mediationId',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: {
            product: {
              normalizer: {
                offers: 'offers',
              },
              stateKey: 'products',
            },
          },
        },
        type: 'REQUEST_DATA_GET_/MEDIATIONS/MEDIATIONID',
      })
    })
  })

  describe('showFailDataNotification', () => {
    it('should dispatch an action to trigger fail data notification', () => {
      // given
      const { showFailDataNotification } = mapDispatchToProps(dispatch, props)

      // when
      showFailDataNotification('my error')

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: {
          text: 'my error',
          type: 'fail',
        },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })

  describe('showSuccessDataNotification', () => {
    it('should dispatch an action to trigger sucess notification display', () => {
      // given
      const { showSuccessDataNotification } = mapDispatchToProps(dispatch, props)

      // when
      showSuccessDataNotification()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: {
          tag: 'mediations-manager',
          text: 'Votre accroche a bien été enregistrée',
          type: 'success',
        },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })

  describe('createOrUpdateMediation', () => {
    it('should dispatch an action to trigger creation or update of mediation', () => {
      // given
      const { createOrUpdateMediation } = mapDispatchToProps(dispatch, props)

      // when
      createOrUpdateMediation(true, {}, {}, jest.fn(), jest.fn())

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/mediations',
          body: {},
          encode: 'multipart/form-data',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'POST',
          stateKey: 'mediations',
        },
        type: 'REQUEST_DATA_POST_MEDIATIONS',
      })
    })
  })
})
