import { useFormikContext } from 'formik'
import { useEffect } from 'react'

import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

const scrollToFirstError = () => {
  const firstErrorElement = document.querySelector<
    HTMLInputElement | HTMLElement
  >('[aria-invalid="true"]')
  const scrollBehavior = doesUserPreferReducedMotion() ? 'auto' : 'smooth'

  // Without the setTimeout, the smooth behavior isn't working
  // cf https://github.com/iamdustan/smoothscroll/issues/28#issuecomment-630722825
  setTimeout(() => {
    firstErrorElement?.focus()
    firstErrorElement?.scrollIntoView({
      behavior: scrollBehavior,
      block: 'center',
      inline: 'center',
    })
  })
}

export const ScrollToFirstErrorAfterSubmit = () => {
  const { isSubmitting, isValid, status } = useFormikContext()

  useEffect(() => {
    if ((isSubmitting && !isValid) || status === 'apiError') {
      scrollToFirstError()
    }
  }, [isValid, isSubmitting, status])

  return null
}
