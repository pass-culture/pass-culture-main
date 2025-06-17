import { describe, expect, it, vi } from 'vitest'

import type { AddressFormValues } from 'commons/core/shared/types'
import { resetReactHookFormAddressFields } from 'commons/utils/resetAddressFields'

describe('resetReactHookFormAddressFields', () => {
  it('calls resetField with each field name and correct default value', () => {
    // Mock resetField function
    const resetField = vi.fn()

    // Call the function with the mock
    resetReactHookFormAddressFields(resetField)

    // Expected fields and default values based on your map
    const expectedCalls: [
      keyof AddressFormValues,
      { defaultValue: string | null },
    ][] = [
      ['street', { defaultValue: '' }],
      ['postalCode', { defaultValue: '' }],
      ['city', { defaultValue: '' }],
      ['latitude', { defaultValue: '' }],
      ['longitude', { defaultValue: '' }],
      ['coords', { defaultValue: '' }],
      ['banId', { defaultValue: '' }],
      ['inseeCode', { defaultValue: null }],
      ['search-addressAutocomplete', { defaultValue: '' }],
      ['addressAutocomplete', { defaultValue: '' }],
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
