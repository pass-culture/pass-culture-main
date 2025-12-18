import { yupResolver } from '@hookform/resolvers/yup'
import { useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import type {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { useSaveOfferLocation } from '../commons/hooks/useSaveOfferLocation'
import type { LocationFormValues } from '../commons/types'
import { getInitialValuesFromOffer } from '../commons/utils/getInitialValuesFromOffer'
import { getValidationSchema } from '../commons/utils/getValidationSchema'
import { LocationForm } from './LocationForm/LocationForm'
import { UpdateWarningDialog } from './UpdateWarningDialog/UpdateWarningDialog'

export interface IndividualOfferLocationScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
  venues: VenueListItemResponseModel[]
}
export const IndividualOfferLocationScreen = ({
  offer,
  venues,
}: IndividualOfferLocationScreenProps) => {
  const saveEditionChangesButtonRef = useRef<HTMLButtonElement>(null)

  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()
  const { hasPublishedOfferWithSameEan, subCategories } =
    useIndividualOfferContext()

  const [isUpdateWarningDialogOpen, setIsUpdateWarningDialogOpen] =
    useState(false)

  const offerVenue = venues.find(
    (v) => v.id.toString() === offer.venue.id.toString()
  )
  assertOrFrontendError(
    offerVenue,
    `'offerVenue' venue with id ${offer.venue.id} not found in venues.`
  )

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
    offerVenue,
  })
  const form = useForm({
    defaultValues: initialValues,
    mode: 'all',
    resolver: yupResolver(validationSchema),
  })

  const { saveAndContinue } = useSaveOfferLocation({
    offer,
    setError: form.setError,
  })

  const updateOffer = async (
    formValues: LocationFormValues,
    shouldSendMail = false
  ): Promise<void> => {
    if (
      offer.hasPendingBookings &&
      form.getFieldState('location').isDirty &&
      !isUpdateWarningDialogOpen
    ) {
      setIsUpdateWarningDialogOpen(true)

      return
    }

    await saveAndContinue({
      formValues,
      shouldSendMail,
    })
  }

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
        })
      )
    }
  }

  return (
    <>
      {isUpdateWarningDialogOpen && (
        <UpdateWarningDialog
          onCancel={() => setIsUpdateWarningDialogOpen(false)}
          onConfirm={(shouldSendMail) =>
            form.handleSubmit((formValues) =>
              updateOffer(formValues, shouldSendMail)
            )()
          }
          refToFocusOnClose={saveEditionChangesButtonRef}
        />
      )}

      <FormProvider key={JSON.stringify(initialValues)} {...form}>
        <form
          onSubmit={form.handleSubmit((formValues) => updateOffer(formValues))}
        >
          <ScrollToFirstHookFormErrorAfterSubmit />

          <FormLayout fullWidthActions>
            <FormLayout.MandatoryInfo />

            <LocationForm offerVenue={offerVenue} />
          </FormLayout>

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled(offer) ||
              !!hasPublishedOfferWithSameEan
            }
            dirtyForm={form.formState.isDirty}
            saveEditionChangesButtonRef={saveEditionChangesButtonRef}
          />
        </form>
      </FormProvider>
      <RouteLeavingGuardIndividualOffer
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
