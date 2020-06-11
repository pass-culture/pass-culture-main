import { mapDispatchToProps } from '../SignOutLinkContainer'

jest.mock('redux-thunk-data', () => {
  const { reinitializeData } = jest.requireActual('fetch-normalize-data')

  return {
    reinitializeData,
  }
})

describe('sign out button container', () => {
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
})
// SUCCESS_DATA_PATCH_USERS/CURRENT
