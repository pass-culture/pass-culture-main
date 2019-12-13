import { mapStateToProps } from '../AppContainer'

describe('src | AppContainer', () => {
  it('should map maintenance status to App', () => {
    // given
    const state = {
      location: {},
      history: {},
      maintenance: { isActivated: true },
    }

    // when
    const result = mapStateToProps(state)

    // then
    expect(result).toHaveProperty('isMaintenanceActivated', true)
  })
})
