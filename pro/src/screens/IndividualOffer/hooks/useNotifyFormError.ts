import type { FormikErrors } from 'formik'
import { useEffect } from 'react'

import { FORM_ERROR_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'

interface UseNotifyFormErrorProps {
  isSubmitting: boolean
  errors: FormikErrors<any>
}

const useNotifyFormError = ({
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

export default useNotifyFormError
