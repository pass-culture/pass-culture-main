import { mapStateToProps } from '../AppContainer'

describe('src | AppContainer', () => {
  it('should map maintenance status to App', () => {
    // Given
    const state = {
      modal: { isActive: true },
      maintenance: { isActivated: true },
    }

    // When
    const result = mapStateToProps(state)

    // Then
    expect(result).toHaveProperty('isMaintenanceActivated', true)
  })

  it('should map the modal status to App', () => {
    // Given
    const state = {
      modal: { isActive: false },
      maintenance: { isActivated: true },
    }

    // When
    const result = mapStateToProps(state)

    // Then
    expect(result).toHaveProperty('modalOpen', false)
  })
})
