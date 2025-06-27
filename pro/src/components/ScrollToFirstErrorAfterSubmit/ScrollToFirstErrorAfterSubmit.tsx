import { useEffect } from 'react'
import { useFormContext } from 'react-hook-form'

import { doesUserPreferReducedMotion } from 'commons/utils/windowMatchMedia'

const scrollToFirstError = () => {
  const firstErrorElement = document.querySelector<
    HTMLInputElement | HTMLElement
  >('[aria-invalid="true"], [data-error="true"]')

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

// Specific to React Hook Form
export const ScrollToFirstHookFormErrorAfterSubmit = () => {
  const {
    formState: { isSubmitting, isValid, errors },
  } = useFormContext()

  useEffect(() => {
    if ((isSubmitting && !isValid) || errors.root?.type === 'apiError') {
      scrollToFirstError()
    }
  }, [isValid, isSubmitting, errors.root?.type])

  return null
}
