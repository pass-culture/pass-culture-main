import { getNationalProgramsForDomains } from '../constants/getNationalProgramsForDomains'

describe('getNationalProgramsForDomains', () => {
  it('should return the union of national programs for multiple domains', () => {
    expect(getNationalProgramsForDomains(['6', '11'])).toHaveLength(4)
  })

  it('should return the national program Olympiade culturelle when no domains are provided', () => {
    expect(getNationalProgramsForDomains([])).toEqual([4])
  })

  it('should return the national program Olympiade culturelle for any domains', () => {
    expect(getNationalProgramsForDomains(['6', '11'])).toEqual(
      expect.arrayContaining([4])
    )

    expect(getNationalProgramsForDomains(['111'])).toEqual(
      expect.arrayContaining([4])
    )
  })
})
