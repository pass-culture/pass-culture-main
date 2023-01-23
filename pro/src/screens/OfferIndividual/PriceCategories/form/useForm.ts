import { useFormik } from 'formik'

import { computeInitialValues } from './computeInitialValues'
import { onSubmit } from './onSubmit'
import { PriceCategoriesFormValues } from './types'
import { validationSchema } from './validationSchema'

export const usePriceCategoriesForm = () => {
  const initialValues = computeInitialValues()

  const form = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit,
  })

  return form
}
