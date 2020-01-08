import maintenanceReducer from '../maintenanceReducer'
import * as config from '../../utils/config'

describe('src | Reducers | Maintenance Reducer', () => {
  it('should have an initial state', () => {
    // When
    const newState = maintenanceReducer()

    // Then
    expect(newState).toStrictEqual({
      isActivated: false,
    })
  })

  describe('when the configuration MAINTENANCE_PAGE_AVAILABLE is true', () => {
    beforeEach(() => {
      config.MAINTENANCE_PAGE_AVAILABLE = true
    })

    describe('when receiving a FAIL_DATA_ event', () => {
      it('should mark maintenance as activated when receiving a 500 status code from a SERVER_ERROR', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 500,
            errors: {},
            error_type: 'SERVER_ERROR',
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: true,
        })
      })

      it('should leave maintenance as activated when receiving a 500 status code from a API_ERROR', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 500,
            errors: {},
            error_type: 'API_ERROR',
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })

      it('should leave maintenance as activated when receiving any error different than SERVER_ERROR', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 404,
            errors: {},
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })
    })

    describe('when receiving a SUCCESS_DATA_ event', () => {
      it('should mark maintenance as deactivated when receiving a success', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/features',
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: true,
            status: 200,
            data: [],
          },
          type: 'SUCCESS_DATA_GET_/FEATURES',
        }

        // When
        const newState = maintenanceReducer({ isActivated: true }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })
    })

  })

  describe('when the configuration MAINTENANCE_PAGE_AVAILABLE is false', () => {
    beforeEach(() => {
      config.MAINTENANCE_PAGE_AVAILABLE = false
    })

    describe('when receiving a FAIL_DATA_ event', () => {
      it('should mark maintenance as not activated', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 500,
            errors: {},
            error_type: 'SERVER_ERROR',
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })

      it('should leave maintenance as activated when receiving a 500 status code from a API_ERROR', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 500,
            errors: {},
            error_type: 'API_ERROR',
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })

      it('should leave maintenance as activated when receiving any error different than SERVER_ERROR', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/offerers/DY',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: false,
            status: 404,
            errors: {},
          },
          type: 'FAIL_DATA_GET_/OFFERERS/DY',
        }

        // When
        const newState = maintenanceReducer({ isActivated: false }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })
    })

    describe('when receiving a SUCCESS_DATA_ event', () => {
      it('should mark maintenance as deactivated when receiving a success', () => {
        // Given
        const action = {
          config: {
            method: 'GET',
            rootUrl: 'http://localhost',
            timeout: 50000,
            apiPath: '/features',
          },
          payload: {
            headers: {
              'content-type': 'application/json',
            },
            ok: true,
            status: 200,
            data: [],
          },
          type: 'SUCCESS_DATA_GET_/FEATURES',
        }

        // When
        const newState = maintenanceReducer({ isActivated: true }, action)

        // Then
        expect(newState).toStrictEqual({
          isActivated: false,
        })
      })
    })
  })
})
