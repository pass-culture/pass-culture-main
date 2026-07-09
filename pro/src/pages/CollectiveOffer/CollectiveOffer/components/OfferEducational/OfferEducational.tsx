import { yupResolver } from '@hookform/resolvers/yup'
import { useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type {
  CollectiveOfferResponseIdModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  type OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from '@/commons/core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { computeInitialValuesFromOffer } from '@/commons/core/OfferEducational/utils/computeInitialValuesFromOffer'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from '@/commons/core/OfferEducational/utils/createOfferPayload'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import {
  createPatchOfferPayload,
  createPatchOfferTemplatePayload,
} from '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferEdition/utils/createPatchOfferPayload'

import styles from './OfferEducational.module.scss'
import { OfferEducationalForm } from './OfferEducationalForm/OfferEducationalForm'
import { useCollectiveOfferImageUpload } from './useCollectiveOfferImageUpload'
import type { DomainOption } from './useOfferEducationalFormData'
import { getOfferEducationalValidationSchema } from './validationSchema'

export interface OfferEducationalProps {
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel

  userOfferer: GetEducationalOffererResponseModel | null
  mode: Mode
  domainsOptions: DomainOption[]
  isTemplate: boolean
}

export const OfferEducational = ({
  offer,
  userOfferer,
  domainsOptions,
  mode,
  isTemplate,
}: OfferEducationalProps): JSX.Element => {
  const offerIdRef = useRef(offer?.id)

  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )
  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed
  const { mutate } = useSWRConfig()

  const { requete: requestId } = queryParamsFromOfferer(location)

  const baseInitialValues = computeInitialValuesFromOffer(
    userOfferer,
    isTemplate,
    selectedPartnerVenue,
    offer,
    selectedPartnerVenue.id.toString(),
    isMarseilleEnabled
  )
  const isOfferCreated = offer !== undefined
  const initialValues =
    mode === Mode.CREATION
      ? applyVenueDefaultsToFormValues(
          baseInitialValues,
          isOfferCreated,
          selectedPartnerVenue
        )
      : baseInitialValues

  if (!isTemplate && isNewCollectivePriceEnabled) {
    initialValues.bookingEmails = null
    initialValues.phone = undefined
    initialValues.contactEmail = undefined
  }

  const onSubmit = async (): Promise<boolean> => {
    let newOrUpdatedOffer:
      | CollectiveOfferResponseIdModel
      | GetCollectiveOfferTemplateResponseModel
      | GetCollectiveOfferResponseModel
      | null = null
    const offerValues = form.watch()
    try {
      if (isTemplate) {
        if (offer === undefined) {
          const payload = createCollectiveOfferTemplatePayload(offerValues)

          newOrUpdatedOffer = await api.createCollectiveOfferTemplate({
            body: payload,
          })

          offerIdRef.current = newOrUpdatedOffer.id
        } else {
          const payload = createPatchOfferTemplatePayload(
            offerValues,
            initialValues
          )
          newOrUpdatedOffer = await api.editCollectiveOfferTemplate({
            path: { offer_id: offer.id },
            body: payload,
          })
        }
      } else if (offer === undefined) {
        const payload = createCollectiveOfferPayload(
          offerValues,
          undefined,
          isNewCollectivePriceEnabled
        )
        newOrUpdatedOffer = await api.createCollectiveOffer({
          body: payload,
        })

        offerIdRef.current = newOrUpdatedOffer.id
      } else {
        const payload = createPatchOfferPayload(
          offerValues,
          initialValues,
          isNewCollectivePriceEnabled
        )

        newOrUpdatedOffer = await api.editCollectiveOffer({
          path: { offer_id: offer.id },
          body: payload,
        })
      }

      assertOrFrontendError(
        offerIdRef.current,
        '`offerIdRef.current` is undefined.'
      )
      await handleImageOnSubmit(offerIdRef.current)

      if (
        offer &&
        (isCollectiveOffer(newOrUpdatedOffer) ||
          isCollectiveOfferTemplate(newOrUpdatedOffer))
      ) {
        await mutate(
          [
            offer.isTemplate
              ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
              : GET_COLLECTIVE_OFFER_QUERY_KEY,
            offer.id,
          ],
          {
            ...newOrUpdatedOffer,
            imageUrl: imageOffer?.url,
            imageCredit: imageOffer?.credit,
          },
          { revalidate: false }
        )
      }

      if (mode === Mode.EDITION) {
        logEvent(
          isTemplate
            ? Events.CLICKED_COLLECTIVE_TEMPLATE_OFFER_MODIFICATION
            : Events.CLICKED_COLLECTIVE_OFFER_MODIFICATION,
          { offerId: offer?.id }
        )
      }

      return true
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400) {
        serializeApiErrors(error.body, form.setError)
      } else {
        snackBar.error(SENT_DATA_ERROR_MESSAGE)
      }

      return false
    }
  }

  const form = useForm<OfferEducationalFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(
      getOfferEducationalValidationSchema(isNewCollectivePriceEnabled)
    ),
    shouldFocusError: false,
    mode: 'onTouched',
  })

  const afterSubmitPath = () => {
    if (!offerIdRef.current) {
      handleUnexpectedError(
        new FrontendError('`offerIdRef.current` is undefined.')
      )

      return undefined
    }

    if (mode === Mode.EDITION && offer !== undefined) {
      return `/offre/${computeURLCollectiveOfferId(
        offer.id,
        offer.isTemplate
      )}/collectif/recapitulatif`
    }

    const requestIdParams = requestId ? `?requete=${requestId}` : ''

    return isTemplate
      ? `/offre/${offerIdRef.current}/collectif/vitrine/creation/recapitulatif`
      : `/offre/${offerIdRef.current}/collectif/stocks${requestIdParams}`
  }
  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({ afterSubmitPath, form, onSubmit })

  return (
    <>
      {offer && (
        <OfferEducationalActions
          className={styles.actions}
          isReadOnly={isVenueClosed}
          offer={offer}
          mode={mode}
        />
      )}
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <OfferEducationalForm
            mode={mode}
            userOfferer={userOfferer}
            domainsOptions={domainsOptions}
            isTemplate={isTemplate}
            imageOffer={imageOffer}
            onImageDelete={onImageDelete}
            onImageUpload={onImageUpload}
            offer={offer}
            isSubmitting={form.formState.isSubmitting}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
