import { mapDispatchToProps } from '../LibrairesProviderFormContainer'

describe('src | components | pages | Venue | VenueProviderManager | form | ProviderForm', () => {
  describe('mapDispatchToProps', () => {
    let dispatch
    let props

    beforeEach(() => {
      dispatch = jest.fn()
      props = {
        match: {
          params: {
            venueId: 'AE',
          },
        },
        providerId: 'AA',
        venueId: 'AC',
        venueSiret: 'AB',
      }
    })

    it('should return an object containing functions to pass to component', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        createVenueProvider: expect.any(Function),
        notify: expect.any(Function),
      })
    })

    describe('createVenueProvider', () => {
      it('should create a venue provider using API', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.createVenueProvider(jest.fn(), jest.fn())

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/venueProviders',
            body: {
              providerId: 'AA',
              venueId: 'AC',
              venueIdAtOfferProvider: 'AB',
            },
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'POST',
          },
          type: 'REQUEST_DATA_POST_/VENUEPROVIDERS',
        })
      })
    })

    describe('notify', () => {
      it('should display a notification', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)
        const errors = [{ error: 'error' }]

        // when
        functions.notify(errors)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            text: 'error',
            type: 'danger',
          },
          type: 'SHOW_NOTIFICATION',
        })
      })
    })
  })
})
