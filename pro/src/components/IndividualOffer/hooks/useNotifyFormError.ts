import type { FormikErrors } from 'formik'
import { useEffect } from 'react'
import { FieldErrors, FieldValues } from 'react-hook-form'

import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'

interface UseNotifyReactFormErrorProps<T extends FieldValues> {
  isSubmitting: boolean
  errors: FieldErrors<T>
}

export function useNotifyReactFormError<T extends FieldValues>({
  isSubmitting,
  errors,
}: UseNotifyReactFormErrorProps<T>): void {
  const notify = useNotification()
  useEffect(() => {
    if (isSubmitting && Object.keys(errors).length > 0) {
      notify.error(FORM_ERROR_MESSAGE)
    }
  }, [Object.keys(errors).length, isSubmitting])
}

interface UseNotifyFormErrorProps {
  isSubmitting: boolean
  errors: FormikErrors<any>
}

export const useNotifyFormError = ({
  isSubmitting,
  errors,
}: UseNotifyFormErrorProps): void => {
  const notify = useNotification()
  useEffect(() => {
    if (isSubmitting && Object.keys(errors).length > 0) {
      notify.error(FORM_ERROR_MESSAGE)
    }
  }, [Object.keys(errors).length, isSubmitting])
}
