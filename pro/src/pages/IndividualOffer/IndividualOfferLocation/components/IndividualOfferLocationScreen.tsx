import { yupResolver } from '@hookform/resolvers/yup'
import { useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { hasFormChanged } from '@/commons/utils/hasFormChanged'
import { localStorageManager } from '@/commons/utils/localStorageManager'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { getIsOfferSubcategoryOnline } from '@/pages/IndividualOffer/commons/getIsOfferSubcategoryOnline'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED } from '../../IndividualOfferInformations/commons/constants'
import type { LocationFormValues } from '../commons/types'
import { getInitialValuesFromOffer } from '../commons/utils/getInitialValuesFromOffer'
import { getValidationSchema } from '../commons/utils/getValidationSchema'
import { toPatchOfferPayload } from '../commons/utils/toPatchOfferPayload'
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
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { hasPublishedOfferWithSameEan, subCategories } =
    useIndividualOfferContext()

  const [isUpdateWarningDialogOpen, setIsUpdateWarningDialogOpen] =
    useState(false)

  const isEvent = subCategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )?.isEvent
  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isOfferSubcategoryOnline = getIsOfferSubcategoryOnline(
    offer,
    subCategories
  )

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
    isOfferSubcategoryOnline,
  })
  const initialValues = getInitialValuesFromOffer(offer, {
    isOfferSubcategoryOnline,
    offerVenue,
  })
  const form = useForm({
    defaultValues: initialValues,
    mode: 'all',
    resolver: yupResolver(validationSchema),
  })

  const updateOffer = async (
    formValues: LocationFormValues,
    shouldSendWarningMail = false
  ): Promise<void> => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      const hasAddressChanged = hasFormChanged({
        form,
        fields: [
          'offerLocation',
          'search-addressAutocomplete',
          'street',
          'postalCode',
          'city',
          'coords',
        ],
        initialValues,
      })

      const shouldDisplayUpdatesWarningModal =
        offer.hasPendingBookings && hasAddressChanged

      if (shouldDisplayUpdatesWarningModal && !isUpdateWarningDialogOpen) {
        setIsUpdateWarningDialogOpen(true)
        return
      }
    }

    try {
      const requestBody = toPatchOfferPayload({
        offer,
        formValues,
        shouldSendWarningMail,
      })
      const response = await api.patchOffer(offer.id, requestBody)

      const receivedOfferId = response.id
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      const nextStepForEdition =
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
      const nextStepForCreation = isMediaPageEnabled
        ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
        : isEvent
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? nextStepForEdition
          : nextStepForCreation

      localStorageManager.setItemIfNone(
        `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`,
        true.toString()
      )

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: receivedOfferId,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
          isOnboarding,
        })
      )
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }

      for (const field in error.body) {
        form.setError(field as keyof LocationFormValues, {
          message: error.body[field],
        })
      }

      notification.error(SENT_DATA_ERROR_MESSAGE)
      return
    }
  }

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
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
          onConfirm={(shouldSendWarningMail) =>
            form.handleSubmit((formValues) =>
              updateOffer(formValues, shouldSendWarningMail)
            )
          }
        />
      )}

      <FormProvider key={JSON.stringify(initialValues)} {...form}>
        <form
          onSubmit={form.handleSubmit((formValues) => updateOffer(formValues))}
        >
          <ScrollToFirstHookFormErrorAfterSubmit />

          <FormLayout fullWidthActions>
            <FormLayout.MandatoryInfo />

            <LocationForm
              offerVenue={offerVenue}
              hasPublishedOfferWithSameEan={!!hasPublishedOfferWithSameEan}
            />
          </FormLayout>

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled(offer.status) ||
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
