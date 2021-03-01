import { mapStateToProps } from '../AppContainer'

describe('src | AppContainer', () => {
  it('should map maintenance status to App', () => {
    // Given
    const state = {
      data: {
        users: [],
      },
      maintenance: { isActivated: true },
    }

    // When
    const result = mapStateToProps(state)

    // Then
    expect(result).toHaveProperty('isMaintenanceActivated', true)
  })
})
