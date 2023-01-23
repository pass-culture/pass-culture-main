import { useFormik } from 'formik'

import { IOfferIndividual } from 'core/Offers/types'

import { computeInitialValues } from './computeInitialValues'
import { onSubmit } from './onSubmit'
import { PriceCategoriesFormValues } from './types'
import { validationSchema } from './validationSchema'

export const usePriceCategoriesForm = (offer: IOfferIndividual) => {
  const initialValues = computeInitialValues(offer)

  const form = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit,
  })

  return form
}
