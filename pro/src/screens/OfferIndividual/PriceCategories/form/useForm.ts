import { useFormik } from 'formik'

import { IOfferIndividual } from 'core/Offers/types'

import { computeInitialValues } from './computeInitialValues'
import { onSubmit } from './onSubmit'
import { PriceCategoriesFormValues } from './types'
import { validationSchema } from './validationSchema'

export const usePriceCategoriesForm = (
  offer: IOfferIndividual,
  onSubmitCallback: () => void,
  setOffer: ((offer: IOfferIndividual | null) => void) | null
) => {
  const initialValues = computeInitialValues(offer)
  const onSubmitWithCallback = (values: PriceCategoriesFormValues) => {
    onSubmit(values, offer, setOffer)
    onSubmitCallback()
  }

  const form = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit: onSubmitWithCallback,
  })

  return form
}
