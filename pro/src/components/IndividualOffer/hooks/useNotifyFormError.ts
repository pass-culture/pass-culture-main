import { FormikErrors } from 'formik'
import { useEffect } from 'react'
import { FieldErrors } from 'react-hook-form'

import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { OffererFormValues } from 'components/SignupJourneyForm/Offerer/Offerer'

interface UseNotifyFormErrorProps {
  isSubmitting: boolean
  errors: FieldErrors<OffererFormValues>
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

interface UseFormikNotifyFormErrorProps {
  isSubmitting: boolean
  errors: FormikErrors<any>
}

export const useFormikNotifyFormError = ({
  isSubmitting,
  errors,
}: UseFormikNotifyFormErrorProps): void => {
  const notify = useNotification()
  useEffect(() => {
    if (isSubmitting && Object.keys(errors).length > 0) {
      notify.error(FORM_ERROR_MESSAGE)
    }
  }, [Object.keys(errors).length, isSubmitting])
}
