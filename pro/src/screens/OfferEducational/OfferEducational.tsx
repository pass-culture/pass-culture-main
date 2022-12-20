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
import { IImageUploaderOfferProps } from './OfferEducationalForm/FormImageUploader/FormImageUploader'
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
  isTemplate: boolean
  imageOffer: IImageUploaderOfferProps['imageOffer']
  onImageUpload: IImageUploaderOfferProps['onImageUpload']
  onImageDelete: IImageUploaderOfferProps['onImageDelete']
  isOfferCreated?: boolean
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
  isTemplate,
  imageOffer,
  onImageUpload,
  onImageDelete,
  isOfferCreated = false,
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
      const visualAccessibility = isOfferCreated
        ? initialValues.accessibility.visual
        : venue?.visualDisabilityCompliant
      const mentalAccessibility = isOfferCreated
        ? initialValues.accessibility.mental
        : venue?.mentalDisabilityCompliant
      const motorAccessibility = isOfferCreated
        ? initialValues.accessibility.motor
        : venue?.motorDisabilityCompliant
      const audioAccessibility = isOfferCreated
        ? initialValues.accessibility.audio
        : venue?.audioDisabilityCompliant

      const email =
        isOfferCreated || !venue?.collectiveEmail
          ? initialValues.email
          : venue?.collectiveEmail
      const notifMails =
        isOfferCreated || initialValues.notificationEmails.length > 1
          ? initialValues.notificationEmails
          : initialValues.email
      const phone =
        isOfferCreated || !venue?.collectivePhone
          ? initialValues.phone
          : venue?.collectivePhone

      const noDisabilityCompliant =
        !visualAccessibility &&
        !mentalAccessibility &&
        !motorAccessibility &&
        !audioAccessibility

      formik.setValues({
        ...formik.values,
        interventionArea:
          venue?.collectiveInterventionArea ??
          DEFAULT_EAC_FORM_VALUES.interventionArea,
        accessibility: {
          visual: Boolean(visualAccessibility),
          mental: Boolean(mentalAccessibility),
          motor: Boolean(motorAccessibility),
          audio: Boolean(audioAccessibility),
          none: noDisabilityCompliant,
        },
        eventAddress: {
          ...formik.values.eventAddress,
          venueId: formik.values.venueId,
        },
        email: email,
        phone: phone,
        notificationEmails: [...notifMails],
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
            isTemplate={isTemplate}
            imageOffer={imageOffer}
            onImageDelete={onImageDelete}
            onImageUpload={onImageUpload}
            isOfferCreated={isOfferCreated}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
