import type { RootState } from '@/commons/store/store'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { type ISnackBarItem, initialState, snackBarAdapter } from '../reducer'
import { listSelector } from '../selectors'

describe('snackBarSelector', () => {
  it('should return empty state when no notification is stored', () => {
    const state = {
      snackBar: initialState,
    } as RootState

    const snackBar = listSelector(state)

    expect(snackBar).toHaveLength(0)
  })

  it('should return notification details when notification is stored', () => {
    const snackBarItem: ISnackBarItem = {
      id: '123',
      variant: SnackBarVariant.SUCCESS,
      text: 'My success message',
      createdAt: '2025-01-01 12:00',
    }

    const state = {
      snackBar: {
        ...initialState,
        list: snackBarAdapter.getInitialState(undefined, [snackBarItem]),
      },
    } as RootState

    const snackBar = listSelector(state)

    expect(snackBar).toHaveLength(1)
    expect(snackBar[0]).toMatchObject({
      variant: SnackBarVariant.SUCCESS,
      text: 'My success message',
    })
  })
})
