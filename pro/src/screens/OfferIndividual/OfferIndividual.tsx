import React from 'react'
import { useFormik, FormikProvider } from 'formik'

import { DEFAULT_INDIVIDUAL_FORM_VALUES } from 'core/Offers'
import { IOfferIndividualFormValues } from 'core/Offers/types'
import { OfferFormStepper } from 'new_components/OfferFormStepper'

import { validationSchema } from './validationSchema'

interface IOfferIndividualProps {
  children: JSX.Element
}

// can get some date or api func from parent route
const OfferIndividual = ({ children }: IOfferIndividualProps): JSX.Element => {
  // GOAL: store all step information here
  const initialValues: IOfferIndividualFormValues = {
    ...DEFAULT_INDIVIDUAL_FORM_VALUES,
    title: 'toto',
  }
  const onSubmit = () => {}

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  return (
    <div>
      <h1 style={{ color: 'blue' }}>screen: OfferIndividual</h1>
      <OfferFormStepper />

      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}></form>
        <div>{children}</div>{' '}
        {/* each step need it access to it own validationSchema */}
        <div>
          <h3> Global actions: prev, next, save </h3>
        </div>
      </FormikProvider>
    </div>
  )
}

export default OfferIndividual
