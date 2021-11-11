import { computeCreditGaugeFilling } from '../computeCreditGaugeFilling'

describe('computeCreditGaugeFilling', () => {
  it('should return step 0 when remainingCredit is between 0 and 9 and creditLimit is 100', () => {
    // Given
    const remainingCredit = 3
    const creditLimit = 100

    // When
    const result = computeCreditGaugeFilling(remainingCredit, creditLimit)

    // Then
    expect(result).toBe(0)
  })

  it('should return step 5 when remainingCredit is between 50 and 59 and creditLimit is 100', () => {
    // Given
    const remainingCredit = 59
    const creditLimit = 100

    // When
    const result = computeCreditGaugeFilling(remainingCredit, creditLimit)

    // Then
    expect(result).toBe(5)
  })

  it('should return step 10 when remainingCredit is equal to creditLimit', () => {
    // Given
    const remainingCredit = 100
    const creditLimit = 100

    // When
    const result = computeCreditGaugeFilling(remainingCredit, creditLimit)

    // Then
    expect(result).toBe(10)
  })

  it('should return step 0 when credit limit is 0', () => {
    // Given
    const remainingCredit = 100
    const creditLimit = 0

    // When
    const result = computeCreditGaugeFilling(remainingCredit, creditLimit)

    // Then
    expect(result).toBe(0)
  })

  it('should never return under zero', () => {
    // Given
    const remainingCredit = -1
    const creditLimit = 100

    // When
    const result = computeCreditGaugeFilling(remainingCredit, creditLimit)

    // Then
    expect(result).toBe(0)
  })
})
