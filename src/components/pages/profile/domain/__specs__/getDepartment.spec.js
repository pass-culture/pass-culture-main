import { getDepartment } from '../getDepartment'

describe('getDepartment', () => {
  it('should return department name & code', () => {
    // given
    const departmentCode = '76'

    // when
    const department = getDepartment(departmentCode)

    // then
    expect(department).toBe('Seine-Maritime (76)')
  })
})
