import getDepartementByCode from '../getDepartementByCode'

describe('getDepartementByCode ', () => {
  it('should return Finistère name', () => {
    expect(getDepartementByCode('29')).toBe('Finistère')
  })

  it('should return Hérault name', () => {
    expect(getDepartementByCode('34')).toBe('Hérault')
  })

  it('should return Bas-Rhin name', () => {
    expect(getDepartementByCode('67')).toBe('Bas-Rhin')
  })

  it('should return Seine-Saint-Denis name', () => {
    expect(getDepartementByCode('93')).toBe('Seine-Saint-Denis')
  })

  it('should return Guadeloupe name', () => {
    expect(getDepartementByCode('971')).toBe('Guadeloupe')
  })

  it('should return Martinique name', () => {
    expect(getDepartementByCode('972')).toBe('Martinique')
  })

  it('should return Guyane name', () => {
    expect(getDepartementByCode('973')).toBe('Guyane')
  })

  it('should return La Réunion name', () => {
    expect(getDepartementByCode('974')).toBe('La Réunion')
  })

  it('should return Saint-Pierre-et-Miquelon name', () => {
    expect(getDepartementByCode('975')).toBe('Saint-Pierre-et-Miquelon')
  })

  it('should return Mayotte name', () => {
    expect(getDepartementByCode('976')).toBe('Mayotte')
  })

  it('should return Finistère name (réécrire)', () => {
    expect(getDepartementByCode('')).toBeNull()
  })
})
