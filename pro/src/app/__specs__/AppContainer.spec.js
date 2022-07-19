import { mapStateToProps } from '../AppContainer'

describe('src | AppContainer', () => {
  it('should map maintenance status to App', () => {
    // Given
    const state = {
      user: {
        initialized: false,
        currentUser: null,
      },
      features: {
        list: [],
        initialized: false,
      },
      maintenance: { isActivated: true },
    }

    // When
    const result = mapStateToProps(state)

    // Then
    expect(result).toHaveProperty('isMaintenanceActivated', true)
  })
})
