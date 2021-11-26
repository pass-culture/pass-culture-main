import { useFormik, FormikProvider } from 'formik'
import React from 'react'

import {
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'

import OfferEducationalForm from './OfferEducationalForm'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalProps {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
  initialValues: IOfferEducationalFormValues
  onSubmit(values: IOfferEducationalFormValues): void
  userOfferers: IUserOfferer[]
}

const OfferEducational = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  initialValues,
  onSubmit,
}: IOfferEducationalProps): JSX.Element => {
  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <OfferEducationalForm
          educationalCategories={educationalCategories}
          educationalSubCategories={educationalSubCategories}
          userOfferers={userOfferers}
        />
      </form>
    </FormikProvider>
  )
}

export default OfferEducational
