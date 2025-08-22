import type {
  AssertTrue,
  ThatSupTypePropsIncludeSubTypeProps,
} from '@/commons/custom_types/test_utils'

import type { PriceTableFormValues } from '../schemas'
import type { PriceTableEntryApiValues } from '../types'

describe('type PriceTableEntryApiValues', () => {
  // This test is a placeholder for TS type-checking tests.
  it('should include type PriceTableFormValues.entries[number] props', () => {
    // @ts-expect-no-error
    type _A = AssertTrue<
      ThatSupTypePropsIncludeSubTypeProps<
        PriceTableEntryApiValues,
        PriceTableFormValues['entries'][number]
      >
    >

    expect(true).toBe(true)
  })
})
