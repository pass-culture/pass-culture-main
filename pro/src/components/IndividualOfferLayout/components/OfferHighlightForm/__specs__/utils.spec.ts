import { describe, expect, it } from 'vitest'

import { getDateTag } from '../utils'

describe('getDateTag', () => {
  it('should return a date range when start and end dates are different', () => {
    // Given
    const startDate = '2025-01-01'
    const endDate = '2025-01-02'

    // When
    const result = getDateTag(startDate, endDate)

    // Then
    expect(result).toBe('01/01/2025 au 02/01/2025')
  })

  it('should return a single date when start and end dates are the same', () => {
    // Given
    const startDate = '2025-01-01'
    const endDate = '2025-01-01'

    // When
    const result = getDateTag(startDate, endDate)

    // Then
    expect(result).toBe('01/01/2025')
  })
})
