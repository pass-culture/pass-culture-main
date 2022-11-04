import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CanOffererCreateCollectiveOffer,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  EducationalCategories,
  Mode,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'

import styles from './OfferEducational.module.scss'
import OfferEducationalForm from './OfferEducationalForm'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalProps {
  categories: EducationalCategories
  initialValues: IOfferEducationalFormValues
  onSubmit(values: IOfferEducationalFormValues): void
  userOfferers: GetEducationalOffererResponseModel[]
  getIsOffererEligible?: CanOffererCreateCollectiveOffer
  mode: Mode
  cancelActiveBookings?: () => void
  setIsOfferActive?: (isActive: boolean) => void
  isOfferBooked?: boolean
  isOfferActive?: boolean
  isOfferCancellable?: boolean
  domainsOptions: SelectOption[]
}

const OfferEducational = ({
  categories,
  userOfferers,
  initialValues,
  onSubmit,
  getIsOffererEligible,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
  isOfferBooked = false,
  isOfferCancellable = false,
  isOfferActive = false,
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

  // FIX ME
  useEffect(() => {
    // update formik values with initial values when initial values
    // are updated after offer update
    resetForm({ values: initialValues })
  }, [initialValues, resetForm])

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
            categories={categories}
            getIsOffererEligible={getIsOffererEligible}
            mode={mode}
            userOfferers={userOfferers}
            domainsOptions={domainsOptions}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
