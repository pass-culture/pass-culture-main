import { checkIfDepartmentIsEligible } from '../checkIfDepartmentIsEligible'

const metropolisEligiblePostalCodes = [
  '08000',
  '67100',
  '25200',
  '34300',
  '58200',
  '71230',
  '93800',
  '94000',
  '84530',
  '22640',
  '29540',
  '35770',
  '56890',
]
const overseasEligiblePostalCodes = ['97310']

describe('check if department is eligible', () => {
  describe('when department is in Metropolis', () => {
    it('should return true if user department is eligible', () => {
      metropolisEligiblePostalCodes.forEach(postalCode => {
        // Given
        const userDepartment = checkIfDepartmentIsEligible(postalCode)

        // Then
        expect(userDepartment).toBe(true)
      })
    })

    it('should return false if user department is not eligible', () => {
      // Given
      const userDepartment = checkIfDepartmentIsEligible('27200')

      // Then
      expect(userDepartment).toBe(false)
    })
  })

  describe('when department is overseas', () => {
    it('should return true if user department is eligible', () => {
      overseasEligiblePostalCodes.forEach(postalCode => {
        // Given
        const userDepartment = checkIfDepartmentIsEligible(postalCode)

        // Then
        expect(userDepartment).toBe(true)
      })
    })

    it('should return false if user department is not eligible', () => {
      // Given
      const userDepartment = checkIfDepartmentIsEligible('97100')

      // Then
      expect(userDepartment).toBe(false)
    })
  })
})
