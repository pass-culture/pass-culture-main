import { useEffect } from 'react'
import { FieldErrors, FieldValues } from 'react-hook-form'

import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'

interface UseNotifyFormErrorProps<T extends FieldValues> {
  isSubmitting: boolean
  errors: FieldErrors<T>
}

export function useNotifyFormError<T extends FieldValues>({
  isSubmitting,
  errors,
}: UseNotifyFormErrorProps<T>): void {
  const notify = useNotification()
  useEffect(() => {
    if (isSubmitting && Object.keys(errors).length > 0) {
      notify.error(FORM_ERROR_MESSAGE)
    }
  }, [Object.keys(errors).length, isSubmitting])
}
