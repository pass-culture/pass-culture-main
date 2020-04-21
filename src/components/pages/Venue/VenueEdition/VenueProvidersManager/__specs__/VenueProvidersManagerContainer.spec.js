import { mapDispatchToProps, mapStateToProps } from '../VenueProvidersManagerContainer'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  describe('mapStateToProps', () => {
    it('should return an object with props', () => {
      // given
      const state = {
        data: {
          providers: [{ id: 'AF', localClass: 'a' }, { id: 'AG', localClass: 'b' }],
          venueProviders: [{ id: 'AE', venueId: 'EE' }],
        },
      }
      const props = {
        venue: { id: 'EE', siret: '12345678901234' },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        providers: [{ id: 'AF', localClass: 'a' }, { id: 'AG', localClass: 'b' }],
        venueProviders: [{ id: 'AE', venueId: 'EE' }],
        venueSiret: '12345678901234'
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
        loadProvidersAndVenueProviders: expect.any(Function),
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
            apiPath: '/providers/AE',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/PROVIDERS/AE',
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
  })
})
