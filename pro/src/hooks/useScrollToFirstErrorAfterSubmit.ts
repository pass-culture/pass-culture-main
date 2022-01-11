import { useFormikContext } from 'formik'
import { useEffect } from 'react'

const scrollToFirstError = () => {
  const firstErrorElement = document.querySelector('[aria-invalid="true"]')

  // Without the setTimeout, the smooth behavior isn't working
  // cf https://github.com/iamdustan/smoothscroll/issues/28#issuecomment-630722825
  setTimeout(
    () =>
      firstErrorElement?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center',
      }),
    0
  )
}

const useScrollToFirstErrorAfterSubmit = (): void => {
  const { isSubmitting, isValid } = useFormikContext()

  useEffect(() => {
    if (isSubmitting && !isValid) {
      scrollToFirstError()
    }
  }, [isValid, isSubmitting])
}

export default useScrollToFirstErrorAfterSubmit
