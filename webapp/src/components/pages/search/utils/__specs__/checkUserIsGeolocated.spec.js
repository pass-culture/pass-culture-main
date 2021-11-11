import { isUserAllowedToSelectCriterion } from '../../../../../utils/geolocation'
import { checkUserIsGeolocated } from '../checkUserIsGeolocated'

jest.mock('../../../../../utils/geolocation', () => ({
  isUserAllowedToSelectCriterion: jest.fn(),
  isGeolocationEnabled: jest.fn(),
}))

describe('components | checkUserIsGeolocated', () => {
  it('should not trigger callback when user is not allowed to select criterion', () => {
    // Given
    isUserAllowedToSelectCriterion.mockReturnValue(false)
    const callback = jest.fn()

    // When
    checkUserIsGeolocated('proximity', null, callback)

    // Then
    expect(callback).toHaveBeenCalledTimes(0)
  })

  it('should trigger callback when user is allowed to select criterion', () => {
    // Given
    isUserAllowedToSelectCriterion.mockReturnValue(true)
    const callback = jest.fn()

    // When
    checkUserIsGeolocated('proximity', null, callback)

    // Then
    expect(callback).toHaveBeenCalledTimes(1)
  })
})
