import { useCallback, useMemo } from 'react'

import { addSnackBar } from '@/commons/store/snackBar/reducer'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { useAppDispatch } from './useAppDispatch'

export const useSnackBar = () => {
  const dispatch = useAppDispatch()

  const notify = useCallback(
    (description: string, variant: SnackBarVariant, targetFocusId?: string) => {
      dispatch(addSnackBar({ description, variant, targetFocusId }))
    },
    [dispatch]
  )

  return useMemo(
    () => ({
      success: (msg: string, targetFocusId?: string) =>
        notify(msg, SnackBarVariant.SUCCESS, targetFocusId),
      error: (msg: string, targetFocusId?: string) =>
        notify(msg, SnackBarVariant.ERROR, targetFocusId),
    }),
    [notify]
  )
}
