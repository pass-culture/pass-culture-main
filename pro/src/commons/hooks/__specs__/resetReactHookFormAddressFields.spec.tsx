import { describe, expect, it, vi } from 'vitest'

import type { AddressFormValues } from '@/commons/core/shared/types'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'

describe('resetReactHookFormAddressFields', () => {
  it('calls resetField with each field name and correct default value', () => {
    // Mock resetField function
    const resetField = vi.fn()

    // Call the function with the mock
    resetReactHookFormAddressFields(resetField)

    // Expected fields and default values based on your map
    const expectedCalls: [
      keyof AddressFormValues,
      defaultValue: string | null,
    ][] = [
      ['street', ''],
      ['postalCode', ''],
      ['city', ''],
      ['latitude', ''],
      ['longitude', ''],
      ['coords', ''],
      ['banId', ''],
      ['inseeCode', null],
      ['search-addressAutocomplete', ''],
      ['addressAutocomplete', ''],
    ]

    // Check the number of calls
    expect(resetField).toHaveBeenCalledTimes(expectedCalls.length)

    // Check each call
    expectedCalls.forEach(([fieldName, defaultValue], index) => {
      expect(resetField).toHaveBeenNthCalledWith(
        index + 1,
        fieldName,
        defaultValue
      )
    })
  })
})
