import { createStore, type RootState } from '@/commons/store/store'

import type { DeepPartial } from '../custom_types/utils'

export const configureTestStore = (
  overrideData: DeepPartial<RootState> = {}
) => {
  return createStore(overrideData as Partial<RootState>).store
}
