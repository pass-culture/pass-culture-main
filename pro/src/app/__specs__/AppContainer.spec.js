import { mapStateToProps } from '../AppContainer'

describe('src | AppContainer', () => {
  it('should map maintenance status to App', () => {
    // Given
    const state = {
      data: {
        users: [],
      },
      user: {
        initialized: false,
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
