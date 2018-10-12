import { getDepartementByCode } from '../getDepartementByCode'

describe('getDepartementByCode ', () => {
  it('should return Finistère name', () => {
    expect(getDepartementByCode('29')).toEqual('Finistère')
  })
  it('should return Hérault name', () => {
    expect(getDepartementByCode('34')).toEqual('Hérault')
  })
  it('should return Bas-Rhin name', () => {
    expect(getDepartementByCode('67')).toEqual('Bas-Rhin')
  })
  it('should return Seine-Saint-Denis name', () => {
    expect(getDepartementByCode('93')).toEqual('Seine-Saint-Denis')
  })
  it('should return Guadeloupe name', () => {
    expect(getDepartementByCode('971')).toEqual('Guadeloupe')
  })
  it('should return Martinique name', () => {
    expect(getDepartementByCode('972')).toEqual('Martinique')
  })
  it('should return Guyane name', () => {
    expect(getDepartementByCode('973')).toEqual('Guyane')
  })
  it('should return La Réunion name', () => {
    expect(getDepartementByCode('974')).toEqual('La Réunion')
  })
  it('should return Saint-Pierre-et-Miquelon name', () => {
    expect(getDepartementByCode('975')).toEqual('Saint-Pierre-et-Miquelon')
  })
  it('should return Mayotte name', () => {
    expect(getDepartementByCode('976')).toEqual('Mayotte')
  })
  it('should return Finistère name', () => {
    expect(getDepartementByCode('')).toEqual(null)
  })
})
