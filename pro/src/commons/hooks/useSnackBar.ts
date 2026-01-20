/* istanbul ignore file */

import { useCallback, useMemo } from 'react'

import { addSnackBar } from '@/commons/store/snackBar/reducer'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { useAppDispatch } from './useAppDispatch'

export const useSnackBar = () => {
  const dispatch = useAppDispatch()

  const notify = useCallback(
    (description: string, variant: SnackBarVariant) => {
      dispatch(addSnackBar({ description, variant }))
    },
    [dispatch]
  )

  return useMemo(
    () => ({
      success: (msg: string) => notify(msg, SnackBarVariant.SUCCESS),
      error: (msg: string) => notify(msg, SnackBarVariant.ERROR),
    }),
    [notify]
  )
}
