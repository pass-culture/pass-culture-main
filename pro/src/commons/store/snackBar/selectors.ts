import {
  type ISnackBarItem,
  snackBarAdapter,
} from '@/commons/store/snackBar/reducer'
import type { RootState } from '@/commons/store/store'

const snackBarSelectors = snackBarAdapter.getSelectors(
  (state: RootState) => state.snackBar.list
)

export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.snackBar.isStickyBarOpen
}

export const listSelector = (state: RootState): ISnackBarItem[] => {
  return snackBarSelectors.selectAll(state)
}
