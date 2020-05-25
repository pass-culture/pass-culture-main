import { mapDispatchToProps } from '../SignoutLinkContainer'

jest.mock('redux-thunk-data', () => {
  const { reinitializeData, requestData } = jest.requireActual('fetch-normalize-data')

  return {
    reinitializeData,
    requestData,
  }
})

describe('signout button container', () => {
  it('should dispatch action to sign out from API', () => {
    // Given
    const dispatch = jest.fn()
    const handleSuccess = jest.fn()

    // when
    mapDispatchToProps(dispatch).signOut(handleSuccess)

    // then
    expect(dispatch).toHaveBeenCalledWith({
      config: {
        apiPath: '/users/signout',
        handleSuccess,
        method: 'GET',
      },
      type: 'REQUEST_DATA_GET_/USERS/SIGNOUT',
    })
  })

  it('should dispatch action to reset seed last request timestamp', () => {
    // Given
    const dispatch = jest.fn()
    const date = Date.now()

    // when
    mapDispatchToProps(dispatch).resetSeedLastRequestTimestamp(date)

    // then
    expect(dispatch).toHaveBeenCalledWith({
      seedLastRequestTimestamp: date,
      type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP',
    })
  })

  it('should dispatch action to reinitialize data except features', () => {
    // Given
    const dispatch = jest.fn()

    // when
    mapDispatchToProps(dispatch).reinitializeDataExceptFeatures()

    // then
    expect(dispatch).toHaveBeenCalledWith({
      config: {
        excludes: ['features'],
      },
      type: 'REINITIALIZE_DATA',
    })
  })

  it('should dispatch action to update read recommendations from API', () => {
    // Given
    const dispatch = jest.fn()
    const readRecommendations = []
    const handleSignOut = jest.fn()

    // when
    mapDispatchToProps(dispatch).updateReadRecommendations(readRecommendations, handleSignOut)

    // then
    expect(dispatch).toHaveBeenCalledWith({
      config: {
        apiPath: '/recommendations/read',
        body: readRecommendations,
        handleFail: handleSignOut,
        handleSuccess: handleSignOut,
        method: 'PUT',
      },
      type: 'REQUEST_DATA_PUT_/RECOMMENDATIONS/READ',
    })
  })
})
