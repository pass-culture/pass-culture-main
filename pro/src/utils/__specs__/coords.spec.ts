import { checkCoords, getCoordsType } from 'utils/coords'

describe('checkCoords', () => {
  it('should validate the latitude, longitude format', () => {
    expect(checkCoords('48.853320, 2.348979')).toBe(true)
    expect(checkCoords('-51.451142, 7.012452')).toBe(true)

    // Test exact limits values that are still valid (-90 <= latitude <= 90 and -180 <= longitude <= 180)
    // (even if there is little chance that an offerer will propose an offer at the exact South Pole's coordinates!)
    expect(checkCoords('90.00000, 180.000000')).toBe(true)
    expect(checkCoords('-90.00000, -180.000000')).toBe(true)
    expect(checkCoords('-90.00000, 180.000000')).toBe(true)
    expect(checkCoords('90.00000, -180.000000')).toBe(true)

    // Test invalid cases
    expect(checkCoords('91.000000, 2.348979')).toBe(false) // Latitude shouldn't be higher than 90
    expect(checkCoords('48.853320, 181.000000')).toBe(false) // Longitude shouldn't be higher than 180
    expect(checkCoords('foobar')).toBe(false)
  })

  it('should validate the DMS format', () => {
    expect(checkCoords(`48°51'12.0"N 2°20'56.3"E`)).toBe(true)
    expect(checkCoords(`48°51'12.0"N, 2°20'56.3"E`)).toBe(false) // Comma is not a valid character
    expect(checkCoords(`48°51'12.0"X 2°20'56.3"E`)).toBe(false) // X is not a valid character
  })
})

describe('getCoordsType', () => {
  it('should return the type of coordinates', () => {
    expect(getCoordsType('48.853320, 2.348979')).toBe('DD') // Decimal degrees
    expect(getCoordsType(`48°51'12.0"N 2°20'56.3"E`)).toBe('DMS') // Degrees, minutes, seconds
    expect(getCoordsType('foobar')).toBe('unknown')
  })
})
