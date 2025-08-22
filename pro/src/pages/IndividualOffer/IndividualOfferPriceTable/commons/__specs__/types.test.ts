import type {
  AssertTrue,
  ThatSupTypePropsIncludeSubTypeProps,
} from '@/commons/custom_types/test_utils'

import type { PriceTableFormValues } from '../schemas'
import type { PriceTableEntryApiValues } from '../types'

// @ts-expect-no-error
type _A = AssertTrue<
  ThatSupTypePropsIncludeSubTypeProps<
    PriceTableEntryApiValues,
    PriceTableFormValues['entries'][number]
  >
>
