import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
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
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
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
  isOfferCreated?: boolean
  venues: VenueListItemResponseModel[]
}

export const OfferEducational = ({
  offer,
  userOfferer,
  domainsOptions,
  mode,
  isTemplate,
  venues,
}: OfferEducationalProps): JSX.Element => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const { mutate } = useSWRConfig()

  const { lieu: venueId, requete: requestId } = queryParamsFromOfferer(location)

  const baseInitialValues = computeInitialValuesFromOffer(
    userOfferer,
    isTemplate,
    venues,
    offer,
    venueId,
    isMarseilleEnabled
  )
  const isOfferCreated = offer !== undefined
  const initialValues =
    mode === Mode.CREATION
      ? applyVenueDefaultsToFormValues(
          baseInitialValues,
          userOfferer,
          isOfferCreated,
          venues
        )
      : baseInitialValues

  const onSubmit = async () => {
    let response = null
    const offerValues = form.watch()
    try {
      if (isTemplate) {
        if (offer === undefined) {
          const payload = createCollectiveOfferTemplatePayload(offerValues)

          response = await api.createCollectiveOfferTemplate(payload)
        } else {
          const payload = createPatchOfferTemplatePayload(
            offerValues,
            initialValues
          )
          response = await api.editCollectiveOfferTemplate(offer.id, payload)
        }
      } else {
        if (offer === undefined) {
          const payload = createCollectiveOfferPayload(offerValues)

          response = await api.createCollectiveOffer(payload)
        } else {
          const payload = createPatchOfferPayload(offerValues, initialValues)
          response = await api.editCollectiveOffer(offer.id, payload)
        }
      }

      const offerId = offer?.id ?? response.id
      await handleImageOnSubmit(offerId)

      if (
        offer &&
        (isCollectiveOffer(response) || isCollectiveOfferTemplate(response))
      ) {
        await mutate(
          [
            offer.isTemplate
              ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
              : GET_COLLECTIVE_OFFER_QUERY_KEY,
            offer.id,
          ],
          {
            ...response,
            imageUrl: imageOffer?.url,
            imageCredit: imageOffer?.credit,
          },
          { revalidate: false }
        )
      }
      if (mode === Mode.EDITION && offer !== undefined) {
        return navigate(
          `/offre/${computeURLCollectiveOfferId(
            offer.id,
            offer.isTemplate
          )}/collectif/recapitulatif`
        )
      }
      const requestIdParams = requestId ? `?requete=${requestId}` : ''
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        isTemplate
          ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
          : `/offre/${offerId}/collectif/stocks${requestIdParams}`
      )
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400) {
        const serializedError = serializeApiErrors(
          error.body,
          {
            contactEmail: 'email',
          },
          {
            bookingEmails: 'notificationEmails',
          }
        )

        ;(serializedError.notificationEmails || []).forEach((error, index) => {
          if (error) {
            form.setError(`notificationEmails.${index}.email`, {
              message: error,
            })
          }
        })
        if (error.body.email && error.body.email.length > 0) {
          form.setError('email', {
            message: error.body.email[0],
          })
        }
      } else {
        snackBar.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const form = useForm<OfferEducationalFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getOfferEducationalValidationSchema()),
    shouldFocusError: false,
    mode: 'onTouched',
  })

  return (
    <>
      {offer && (
        <OfferEducationalActions
          className={styles.actions}
          offer={offer}
          mode={mode}
        />
      )}
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <OfferEducationalForm
            mode={mode}
            userOfferer={userOfferer}
            domainsOptions={domainsOptions}
            isTemplate={isTemplate}
            imageOffer={imageOffer}
            onImageDelete={onImageDelete}
            onImageUpload={onImageUpload}
            isOfferCreated={isOfferCreated}
            offer={offer}
            isSubmitting={form.formState.isSubmitting}
            venues={venues}
          />
        </form>
      </FormProvider>
      <RouteLeavingGuardCollectiveOfferCreation
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
