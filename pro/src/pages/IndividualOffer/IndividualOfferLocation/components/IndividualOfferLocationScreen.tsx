import { yupResolver } from '@hookform/resolvers/yup'
import { useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { SynchronizedBanner } from '../../components/SynchronizedBanner/SynchronizedBanner'
import { useSaveOfferLocation } from '../commons/hooks/useSaveOfferLocation'
import type { LocationFormValues } from '../commons/types'
import { getInitialValuesFromOffer } from '../commons/utils/getInitialValuesFromOffer'
import { getValidationSchema } from '../commons/utils/getValidationSchema'
import { LocationForm } from './LocationForm/LocationForm'
import { UpdateWarningDialog } from './UpdateWarningDialog/UpdateWarningDialog'

export interface IndividualOfferLocationScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}
export const IndividualOfferLocationScreen = ({
  offer,
}: IndividualOfferLocationScreenProps) => {
  const [isSaving, setIsSaving] = useState(false)
  const updateWarningDialogDeferredCallRef = useRef<
    ((shouldSendMail: boolean | null) => void) | null
  >(null)

  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const mode = useOfferWizardMode()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')
  const { hasPublishedOfferWithSameEan, subCategories } =
    useIndividualOfferContext()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed
  const [isUpdateWarningDialogOpen, setIsUpdateWarningDialogOpen] =
    useState(false)

  const offerSubcategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )
  assertOrFrontendError(
    offerSubcategory,
    `'offerSubcategory' with id "${offer.subcategoryId}" not found in subCategories.`
  )

  const validationSchema = getValidationSchema({
    isDigital: offer.isDigital,
  })
  const initialValues = getInitialValuesFromOffer(offer, {
    offerVenue: selectedPartnerVenue,
  })
  const form = useForm({
    defaultValues: initialValues,
    mode: 'onBlur',
    resolver: yupResolver(validationSchema),
  })

  const { save } = useSaveOfferLocation({
    offer,
    setError: form.setError,
  })

  const updateOffer = async (
    formValues: LocationFormValues
  ): Promise<boolean> => {
    let shouldSendMail: boolean | null = null

    if (offer.hasPendingBookings && form.getFieldState('location').isDirty) {
      setIsUpdateWarningDialogOpen(true)
      // [Deferred Pattern] Pause this submit until the user answers the dialog:
      // we stash the promise's resolve in the ref, wait for it,
      // and continue once the dialog's confirm/cancel handler runs it.
      shouldSendMail = await new Promise<boolean | null>((resolve) => {
        updateWarningDialogDeferredCallRef.current = resolve
      })
      setIsUpdateWarningDialogOpen(false)

      // If the user cancelled the dialog, let's cancel the update
      if (shouldSendMail === null) {
        return false
      }
    }

    // This state is used to disable the action bar buttons while the save is in progress,
    // we cannot use the form's isSubmitting state because it disables the button even when cancelling the dialog
    // which conduct to loosing the focus on the button
    setIsSaving(true)
    try {
      await save({ formValues, shouldSendMail: shouldSendMail ?? false })
      return true
    } finally {
      setIsSaving(false)
    }
  }

  const afterSubmitPath = getAfterSubmitPath({
    offerId: offer.id,
    mode,
    isOnboarding,
    isOfferExposureEnabled,
    currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
    followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
  })
  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      form,
      onSubmit: updateOffer,
    })

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
          isOfferExposureEnabled,
        })
      )
    }
  }

  return (
    <>
      <UpdateWarningDialog
        onCancel={() => {
          setIsUpdateWarningDialogOpen(false)
          updateWarningDialogDeferredCallRef.current?.(null)
        }}
        message="Vous avez modifié l’adresse."
        onConfirm={(shouldSendMail) =>
          updateWarningDialogDeferredCallRef.current?.(shouldSendMail)
        }
        isOpen={isUpdateWarningDialogOpen}
      />

      <FormProvider key={JSON.stringify(initialValues)} {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <ScrollToFirstHookFormErrorAfterSubmit />

          {isOfferSynchronized(offer) && (
            <SynchronizedBanner providerName={offer?.lastProvider?.name} />
          )}
          <FormLayout fullWidthActions>
            <FormLayout.MandatoryInfo />

            <LocationForm />
          </FormLayout>

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION}
            isDisabled={
              isSaving ||
              isOfferDisabled(offer) ||
              !!hasPublishedOfferWithSameEan ||
              (isOfferExposureEnabled &&
                !form.formState.isDirty &&
                mode !== OFFER_WIZARD_MODE.CREATION) ||
              isVenueClosed
            }
            dirtyForm={form.formState.isDirty}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
