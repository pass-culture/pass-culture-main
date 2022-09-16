import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import {
  CanOffererCreateCollectiveOffer,
  DEFAULT_EAC_FORM_VALUES,
  GetEducationalDomainsAdapter,
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
  Mode,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import OfferEducationalActions from 'new_components/OfferEducationalActions'

import styles from './OfferEducational.module.scss'
import OfferEducationalForm from './OfferEducationalForm'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalProps {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
  initialValues: IOfferEducationalFormValues
  onSubmit(values: IOfferEducationalFormValues): void
  userOfferers: GetEducationalOffererResponseModel[]
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
  isOfferCancellable?: boolean
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
  isOfferCancellable = false,
  isOfferActive = false,
  getEducationalDomainsAdapter,
}: IOfferEducationalProps): JSX.Element => {
  const [domainsOptions, setDomainsOptions] = useState<SelectOption[]>([])
  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
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

  useEffect(() => {
    if (
      formik.values.offererId &&
      formik.values.venueId &&
      mode === Mode.CREATION
    ) {
      const venue = userOfferers
        .find(({ id }) => id === formik.values.offererId)
        ?.managedVenues?.find(({ id }) => id === formik.values.venueId)

      const noDisabilityCompliant =
        !venue?.visualDisabilityCompliant &&
        !venue?.mentalDisabilityCompliant &&
        !venue?.motorDisabilityCompliant &&
        !venue?.audioDisabilityCompliant

      formik.setValues({
        ...formik.values,
        interventionArea:
          venue?.collectiveInterventionArea ??
          DEFAULT_EAC_FORM_VALUES.interventionArea,
        accessibility: {
          visual: Boolean(venue?.visualDisabilityCompliant),
          mental: Boolean(venue?.mentalDisabilityCompliant),
          motor: Boolean(venue?.motorDisabilityCompliant),
          audio: Boolean(venue?.audioDisabilityCompliant),
          none: noDisabilityCompliant,
        },
        eventAddress: {
          ...formik.values.eventAddress,
          venueId: formik.values.venueId,
        },
      })
    }
  }, [formik.values.venueId, formik.values.offererId])

  return (
    <>
      {shouldShowOfferActions && (
        <OfferEducationalActions
          cancelActiveBookings={cancelActiveBookings}
          className={styles.actions}
          isBooked={isOfferBooked}
          isCancellable={isOfferCancellable}
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
