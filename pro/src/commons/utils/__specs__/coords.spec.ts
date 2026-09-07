import { checkCoords, getCoordsType, parseDms } from '@/commons/utils/coords'

describe('checkCoords', () => {
  it.each([
    '48.853320, 2.348979',
    '-51.451142, 7.012452',
    '90.00000, 180.000000',
    '-90.00000, -180.000000',
    '-90.00000, 180.000000',
    '90.00000, -180.000000',
  ])('should validate valid coordinate %s', (coords) => {
    expect(checkCoords(coords)).toBe(true)
  })

  it.each(['91.000000, 2.348979', '48.853320, 181.000000', 'foobar'])(
    'should reject invalid coordinate %s',
    (coords) => {
      expect(checkCoords(coords)).toBe(false)
    }
  )

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
describe('parseDms', () => {
  describe('valid coordinates', () => {
    it.each([
      // Examples of standard DMS formats
      { input: '46°59′5″ N', expected: 46.9847, precision: 4 },
      { input: '122°54′8″ W', expected: -122.9022, precision: 4 },
      { input: '0°0′0″ N', expected: 0, precision: 4 },
      { input: '0°59′59″ E', expected: 0.9997, precision: 4 },

      // Examples of DMS formats with alternative separators (colons, 'd', standard quotes)
      { input: '40:26:46.302N', expected: 40.44619, precision: 5 },
      { input: '40d26\'46.3"S', expected: -40.44619, precision: 5 },
      { input: '40° 26\' 46.3" W', expected: -40.44619, precision: 5 },

      // Examples of direct decimal degrees without minutes/seconds
      { input: '40.446195N', expected: 40.446195, precision: 6 },
      { input: '-122.9022', expected: -122.9022, precision: 4 },
    ])('parses "$input" to $expected', ({ input, expected, precision }) => {
      expect(parseDms(input)).toBeCloseTo(expected, precision)
    })
  })

  describe('invalid coordinates', () => {
    it.each([
      { input: '' },
      { input: '  ' },
      { input: 'foobar' },
      { input: 'abc°def′ghi″ N' },
    ])('returns NaN for invalid input "$input"', ({ input }) => {
      expect(parseDms(input)).toBeNaN()
    })
  })
})
