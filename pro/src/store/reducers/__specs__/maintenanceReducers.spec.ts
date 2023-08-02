import maintenanceReducer from '../maintenanceReducer'

describe('maintenanceReducer', () => {
  it('should have an initial state', () => {
    const newState = maintenanceReducer()

    expect(newState).toStrictEqual({ isActivated: false })
  })

  it('should mark maintenance as activated when receiving a 503 status code from a SERVER_ERROR', () => {
    const action = {
      config: {
        method: 'GET',
        rootUrl: 'https://localhost',
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
        status: 503,
        errors: {},
        error_type: 'SERVER_ERROR',
      },
      type: 'FAIL_DATA_GET_/OFFERERS/DY',
    }

    const newState = maintenanceReducer({ isActivated: false }, action)

    expect(newState).toStrictEqual({
      isActivated: true,
    })
  })

  it('should leave maintenance as activated when receiving a 503 status code from a API_ERROR', () => {
    const action = {
      config: {
        method: 'GET',
        rootUrl: 'https://localhost',
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
        status: 503,
        errors: {},
        error_type: 'API_ERROR',
      },
      type: 'FAIL_DATA_GET_/OFFERERS/DY',
    }

    const newState = maintenanceReducer({ isActivated: false }, action)

    expect(newState).toStrictEqual({
      isActivated: false,
    })
  })

  it('should leave maintenance as activated when receiving any error different than SERVER_ERROR', () => {
    const action = {
      config: {
        method: 'GET',
        rootUrl: 'https://localhost',
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

    const newState = maintenanceReducer({ isActivated: false }, action)

    expect(newState).toStrictEqual({
      isActivated: false,
    })
  })

  it('should mark maintenance as deactivated when receiving a success', () => {
    const action = {
      config: {
        method: 'GET',
        rootUrl: 'https://localhost',
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

    const newState = maintenanceReducer({ isActivated: false }, action)

    expect(newState).toStrictEqual({
      isActivated: false,
    })
  })
})
