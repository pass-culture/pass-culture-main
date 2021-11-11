import { _getDepartmentByCode, getDepartment } from '../getDepartment'

describe('department', () => {
  it('should return department name & code', () => {
    // given
    const departmentCode = '76'

    // when
    const department = getDepartment(departmentCode)

    // then
    expect(department).toBe('Seine-Maritime (76)')
  })
})

describe('departement by code', () => {
  it('should return Finistère name', () => {
    expect(_getDepartmentByCode('29')).toBe('Finistère')
  })

  it('should return Hérault name', () => {
    expect(_getDepartmentByCode('34')).toBe('Hérault')
  })

  it('should return Bas-Rhin name', () => {
    expect(_getDepartmentByCode('67')).toBe('Bas-Rhin')
  })

  it('should return Seine-Saint-Denis name', () => {
    expect(_getDepartmentByCode('93')).toBe('Seine-Saint-Denis')
  })

  it('should return Guadeloupe name', () => {
    expect(_getDepartmentByCode('971')).toBe('Guadeloupe')
  })

  it('should return Martinique name', () => {
    expect(_getDepartmentByCode('972')).toBe('Martinique')
  })

  it('should return Guyane name', () => {
    expect(_getDepartmentByCode('973')).toBe('Guyane')
  })

  it('should return La Réunion name', () => {
    expect(_getDepartmentByCode('974')).toBe('La Réunion')
  })

  it('should return Saint-Pierre-et-Miquelon name', () => {
    expect(_getDepartmentByCode('975')).toBe('Saint-Pierre-et-Miquelon')
  })

  it('should return Mayotte name', () => {
    expect(_getDepartmentByCode('976')).toBe('Mayotte')
  })

  it('should return nothing when bad code given', () => {
    expect(_getDepartmentByCode('999')).toBe('')
  })
})
