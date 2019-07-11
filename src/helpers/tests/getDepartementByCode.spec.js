import { getDepartementByCode } from '../getDepartementByCode'

describe('getDepartementByCode ', () => {
  it('should return Finistère name', () => {
    expect(getDepartementByCode('29')).toStrictEqual('Finistère')
  })

  it('should return Hérault name', () => {
    expect(getDepartementByCode('34')).toStrictEqual('Hérault')
  })

  it('should return Bas-Rhin name', () => {
    expect(getDepartementByCode('67')).toStrictEqual('Bas-Rhin')
  })

  it('should return Seine-Saint-Denis name', () => {
    expect(getDepartementByCode('93')).toStrictEqual('Seine-Saint-Denis')
  })

  it('should return Guadeloupe name', () => {
    expect(getDepartementByCode('971')).toStrictEqual('Guadeloupe')
  })

  it('should return Martinique name', () => {
    expect(getDepartementByCode('972')).toStrictEqual('Martinique')
  })

  it('should return Guyane name', () => {
    expect(getDepartementByCode('973')).toStrictEqual('Guyane')
  })

  it('should return La Réunion name', () => {
    expect(getDepartementByCode('974')).toStrictEqual('La Réunion')
  })

  it('should return Saint-Pierre-et-Miquelon name', () => {
    expect(getDepartementByCode('975')).toStrictEqual('Saint-Pierre-et-Miquelon')
  })

  it('should return Mayotte name', () => {
    expect(getDepartementByCode('976')).toStrictEqual('Mayotte')
  })

  it('should return Finistère name (réécrire)', () => {
    expect(getDepartementByCode('')).toStrictEqual(null)
  })
})
