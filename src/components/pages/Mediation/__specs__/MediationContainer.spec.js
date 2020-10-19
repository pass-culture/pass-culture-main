import { mapDispatchToProps } from '../MediationContainer'
import { mapStateToProps } from '../MediationContainer'

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
        showOfferModificationErrorNotification: expect.any(Function),
        showOfferModificationValidationNotification: expect.any(Function),
        createOrUpdateMediation: expect.any(Function),
      })
    })
  })

  describe('getOffer', () => {
    it('should retrieve offer with offerId', () => {
      // given
      const { getOffer } = mapDispatchToProps(dispatch, props)
      const offerId = 'offerId'

      // when
      getOffer(offerId)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/offers/offerId',
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
      const mediationId = 'mediationId'
      const handleSuccess = jest.fn()
      const handleFail = jest.fn()

      // when
      getMediation(mediationId, handleSuccess, handleFail)

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

  describe('showOfferModificationErrorNotification', () => {
    it('should dispatch an action to trigger fail data notification', () => {
      // given
      const { showOfferModificationErrorNotification } = mapDispatchToProps(dispatch, props)
      const error = 'my error'

      // when
      showOfferModificationErrorNotification(error)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: {
          text: 'my error',
          type: 'fail',
        },
        type: 'SHOW_NOTIFICATION_V1',
      })
    })
  })

  describe('showOfferModificationValidationNotification', () => {
    it('should dispatch an action to trigger sucess notification display', () => {
      // given
      const { showOfferModificationValidationNotification } = mapDispatchToProps(dispatch, props)

      // when
      showOfferModificationValidationNotification()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: {
          tag: 'mediations-manager',
          text:
            'Votre offre a bien été modifiée. Cette offre peut mettre quelques minutes pour être disponible dans l’application.',
          type: 'success',
        },
        type: 'SHOW_NOTIFICATION_V1',
      })
    })
  })

  describe('createOrUpdateMediation', () => {
    it('should dispatch an action to trigger creation of mediation', () => {
      // given
      const { createOrUpdateMediation } = mapDispatchToProps(dispatch, props)
      const isNew = true
      const mediation = {}
      const body = {}
      const handleFailData = jest.fn()
      const handleSucessData = jest.fn()

      // when
      createOrUpdateMediation(isNew, mediation, body, handleFailData, handleSucessData)

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

    it('should dispatch an action to trigger update of mediation', () => {
      // given
      const { createOrUpdateMediation } = mapDispatchToProps(dispatch, props)
      const isNew = false
      const mediation = { id: 'mediationId' }
      const body = {}
      const handleFailData = jest.fn()
      const handleSucessData = jest.fn()

      // when
      createOrUpdateMediation(isNew, mediation, body, handleFailData, handleSucessData)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/mediations/mediationId',
          body: {},
          encode: 'multipart/form-data',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'PATCH',
          stateKey: 'mediations',
        },
        type: 'REQUEST_DATA_PATCH_MEDIATIONS',
      })
    })
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          offers: [],
          venues: {
            find: jest.fn(),
          },
          offerers: {
            find: jest.fn(),
          },
          mediations: {
            find: jest.fn(),
          },
        },
      }

      const ownProps = {
        match: {
          params: {
            mediationId: 'mediationId',
            offerId: 'offerId',
          },
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        mediation: undefined,
        offer: undefined,
        offerer: undefined,
      })
    })
  })
})
