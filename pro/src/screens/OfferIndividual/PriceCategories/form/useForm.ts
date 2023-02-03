import { useFormik } from 'formik'

import { IOfferIndividual } from 'core/Offers/types'

import { computeInitialValues } from './computeInitialValues'
import { onSubmit } from './onSubmit'
import { PriceCategoriesFormValues } from './types'
import { validationSchema } from './validationSchema'

export const usePriceCategoriesForm = (
  offer: IOfferIndividual,
  onSubmitCallback: () => void,
  setOffer: ((offer: IOfferIndividual | null) => void) | null,
  notifyError: (msg: string) => void
) => {
  const initialValues = computeInitialValues(offer)

  const onSubmitWithCallback = async (values: PriceCategoriesFormValues) => {
    try {
      await onSubmit(values, offer, setOffer)
      onSubmitCallback()
    } catch (error) {
      if (error instanceof Error) {
        notifyError(error?.message)
      }
    }
  }

  const form = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit: onSubmitWithCallback,
  })

  return form
}
