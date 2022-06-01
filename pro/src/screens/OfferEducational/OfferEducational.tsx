import { FormikProvider, useFormik } from 'formik'
import {
  GetIsOffererEligible,
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
  IUserOfferer,
  Mode,
} from 'core/OfferEducational'
import React, { useEffect } from 'react'

import OfferEducationalActions from 'new_components/OfferEducationalActions'
import OfferEducationalForm from './OfferEducationalForm'
import { SelectOption } from 'custom_types/form'
import styles from './OfferEducational.module.scss'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalProps {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
  initialValues: IOfferEducationalFormValues
  onSubmit(values: IOfferEducationalFormValues): void
  userOfferers: IUserOfferer[]
  getIsOffererEligible?: GetIsOffererEligible
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
  domainsOptions: SelectOption[]
  enableEducationalDomains: boolean
}

const OfferEducational = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  initialValues,
  onSubmit,
  getIsOffererEligible,
  notify,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
  isOfferBooked = false,
  isOfferActive = false,
  enableEducationalDomains,
  domainsOptions,
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
            getIsOffererEligible={getIsOffererEligible}
            mode={mode}
            notify={notify}
            userOfferers={userOfferers}
            enableEducationalDomains={enableEducationalDomains}
            domainsOptions={domainsOptions}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
