import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import {
  CanOffererCreateCollectiveOffer,
  GetEducationalDomainsAdapter,
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
  IUserOfferer,
  Mode,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import OfferEducationalActions from 'new_components/OfferEducationalActions'

import styles from './OfferEducational.module.scss'
import OfferEducationalForm from './OfferEducationalForm'
import {
  validationSchema,
  validationSchemaWithInterventionArea,
} from './validationSchema'

export interface IOfferEducationalProps {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
  initialValues: IOfferEducationalFormValues
  onSubmit(values: IOfferEducationalFormValues): void
  userOfferers: IUserOfferer[]
  getIsOffererEligible?: CanOffererCreateCollectiveOffer
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
  getEducationalDomainsAdapter: GetEducationalDomainsAdapter
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
  getEducationalDomainsAdapter,
}: IOfferEducationalProps): JSX.Element => {
  const enableInterventionZone = useActiveFeature(
    'ENABLE_INTERVENTION_ZONE_COLLECTIVE_OFFER'
  )

  const [domainsOptions, setDomainsOptions] = useState<SelectOption[]>([])
  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema: enableInterventionZone
      ? validationSchemaWithInterventionArea
      : validationSchema,
  })

  const shouldShowOfferActions =
    (mode === Mode.EDITION || mode === Mode.READ_ONLY) &&
    setIsOfferActive &&
    cancelActiveBookings

  // FIX ME
  useEffect(() => {
    // update formik values with initial values when initial values
    // are updated after offer update
    resetForm({ values: initialValues })
  }, [initialValues, resetForm])

  useEffect(() => {
    getEducationalDomainsAdapter().then(result => {
      setDomainsOptions(result.payload)
    })
  }, [])

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
            domainsOptions={domainsOptions}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
