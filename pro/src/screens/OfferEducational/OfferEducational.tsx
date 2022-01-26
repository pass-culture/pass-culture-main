import { useFormik, FormikProvider } from 'formik'
import React, { useEffect } from 'react'

import {
  GetIsOffererEligibleToEducationalOffer,
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
  IUserOfferer,
  Mode,
} from 'core/OfferEducational'
import OfferEducationalActions from 'new_components/OfferEducationalActions'

import styles from './OfferEducational.module.scss'
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
  mode: Mode
  cancelActiveBookings?: () => void
  setIsOfferActive?: (isActive: boolean) => void
  isOfferBooked?: boolean
  isOfferActive?: boolean
}

const OfferEducational = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  initialValues,
  onSubmit,
  getIsOffererEligibleToEducationalOfferAdapter,
  notify,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
  isOfferBooked = false,
  isOfferActive = false,
}: IOfferEducationalProps): JSX.Element => {
  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  const shouldShowOfferActions =
    (mode === Mode.EDITION || mode === Mode.READ_ONLY) &&
    setIsOfferActive &&
    cancelActiveBookings

  useEffect(() => {
    // update formik values with initial values when initial values
    // are updated after offer update
    resetForm({ values: initialValues })
  }, [initialValues, resetForm])

  return (
    <>
      {shouldShowOfferActions && (
        <OfferEducationalActions
          cancelActiveBookings={cancelActiveBookings}
          className={styles.actions}
          isBooked={isOfferBooked}
          isOfferActive={isOfferActive}
          setIsOfferActive={setIsOfferActive}
        />
      )}
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}>
          <OfferEducationalForm
            educationalCategories={educationalCategories}
            educationalSubCategories={educationalSubCategories}
            getIsOffererEligibleToEducationalOfferAdapter={
              getIsOffererEligibleToEducationalOfferAdapter
            }
            mode={mode}
            notify={notify}
            userOfferers={userOfferers}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
