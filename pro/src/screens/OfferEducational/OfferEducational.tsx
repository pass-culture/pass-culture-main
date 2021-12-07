import { useFormik, FormikProvider } from 'formik'
import React from 'react'

import {
  GetIsOffererEligibleToEducationalOffer,
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
  getIsOffererEligibleToEducationalOfferAdapter?: GetIsOffererEligibleToEducationalOffer
  notify: {
    success: (msg: string | null) => void
    error: (msg: string | null) => void
    pending: (msg: string | null) => void
    information: (msg: string | null) => void
  }
  isEdition?: boolean
}

const OfferEducational = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  initialValues,
  onSubmit,
  getIsOffererEligibleToEducationalOfferAdapter,
  notify,
  isEdition = false,
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
          getIsOffererEligibleToEducationalOfferAdapter={
            getIsOffererEligibleToEducationalOfferAdapter
          }
          isEdition={isEdition}
          notify={notify}
          userOfferers={userOfferers}
        />
      </form>
    </FormikProvider>
  )
}

export default OfferEducational
