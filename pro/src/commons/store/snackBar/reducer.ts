import {
  createEntityAdapter,
  createSlice,
  type EntityState,
  type PayloadAction,
} from '@reduxjs/toolkit'
import { format } from 'date-fns'
import { v4 as uuidv4 } from 'uuid'

import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import type { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

export interface ISnackBarItem {
  text: string
  variant: SnackBarVariant
  id: string
  createdAt: string
}

interface SnackBarPayload {
  text: string
  variant: SnackBarVariant
}

export const snackBarAdapter = createEntityAdapter({
  selectId: (snackBarItem: ISnackBarItem) => snackBarItem.id,
})

export interface SnackBarState {
  isStickyBarOpen: boolean
  list: EntityState<ISnackBarItem, string>
}

export const initialState: SnackBarState = {
  isStickyBarOpen: false,
  list: snackBarAdapter.getInitialState(),
}

const snackBarSlice = createSlice({
  name: 'snackBar',
  initialState,
  reducers: {
    setIsStickyBarOpen: (state, action: PayloadAction<boolean>) => {
      state.isStickyBarOpen = action.payload
    },
    /**
     * Add a snackBar to the list.
     */
    addSnackBar: {
      reducer(state, action: PayloadAction<ISnackBarItem>) {
        snackBarAdapter.addOne(state.list, action.payload)
      },
      prepare(payload: SnackBarPayload) {
        return {
          payload: {
            ...payload,
            id: uuidv4(),
            createdAt: format(new Date(), FORMAT_DD_MM_YYYY_HH_mm),
          },
        }
      },
    },
    /**
     * Remove a snackBar from the list.
     *
     * @param action.payload ID of the snackBar to remove.
     */
    removeSnackBar(state, action: PayloadAction<string>) {
      snackBarAdapter.removeOne(state.list, action.payload)
    },
    /**
     * Clear the list of snackBars.
     */
    clearList: (state) => {
      snackBarAdapter.removeAll(state.list)
    },
  },
})

export const snackBarReducer = snackBarSlice.reducer

export const { setIsStickyBarOpen, addSnackBar, removeSnackBar, clearList } =
  snackBarSlice.actions
