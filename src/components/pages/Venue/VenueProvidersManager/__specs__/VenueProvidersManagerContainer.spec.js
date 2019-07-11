import {
  mapDispatchToProps,
  mapStateToProps,
} from '../VenueProvidersManagerContainer'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  describe('mapStateToProps', () => {
    it('should return an object with props', () => {
      // given
      const state = {
        data: {
          providers: [
            { id: 'AF', localClass: 'a' },
            { id: 'AG', localClass: 'b' },
          ],
          venueProviders: [{ id: 'AE', venueId: 'EE' }],
        },
      }
      const props = {
        venue: { id: 'EE' },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        providers: [
          { id: 'AF', localClass: 'a' },
          { id: 'AG', localClass: 'b' },
        ],
        venueProviders: [{ id: 'AE', venueId: 'EE' }],
      })
    })
  })

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
      }
    })

    it('should return an object containing functions to pass to component', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        createVenueProvider: expect.any(Function),
        loadProvidersAndVenueProviders: expect.any(Function),
        notify: expect.any(Function),
      })
    })

    describe('createVenueProvider', () => {
      it('should create a venue provider using API', () => {
        // given
        const payload = {
          providerId: 'AA',
          venueIdAtOfferProvider: 'AB',
          venueId: 'AC',
        }
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.createVenueProvider(jest.fn(), jest.fn(), payload)

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

    describe('loadProvidersAndVenueProviders', () => {
      it('should load providers and venue providers using API', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.loadProvidersAndVenueProviders()

        // then
        expect(dispatch.mock.calls[0][0]).toStrictEqual({
          config: {
            apiPath: '/providers',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/PROVIDERS',
        })
        expect(dispatch.mock.calls[1][0]).toStrictEqual({
          config: {
            apiPath: '/venueProviders?venueId=AE',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/VENUEPROVIDERS?VENUEID=AE',
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
            type: 'fail',
          },
          type: 'SHOW_NOTIFICATION',
        })
      })
    })
  })
})
