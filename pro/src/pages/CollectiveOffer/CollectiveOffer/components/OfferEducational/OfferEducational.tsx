import { FormikProvider, useFormik } from 'formik'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from 'commons/core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { computeInitialValuesFromOffer } from 'commons/core/OfferEducational/utils/computeInitialValuesFromOffer'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from 'commons/core/OfferEducational/utils/createOfferPayload'
import {
  FORM_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { queryParamsFromOfferer } from 'commons/utils/queryParamsFromOfferer'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  createPatchOfferPayload,
  createPatchOfferTemplatePayload,
} from 'pages/CollectiveOffer/CollectiveOffer/CollectiveOfferEdition/utils/createPatchOfferPayload'

import styles from './OfferEducational.module.scss'
import { OfferEducationalForm } from './OfferEducationalForm/OfferEducationalForm'
import { useCollectiveOfferImageUpload } from './useCollectiveOfferImageUpload'
import { DomainOption } from './useOfferEducationalFormData'
import { getOfferEducationalValidationSchema } from './validationSchema'

export interface OfferEducationalProps {
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel

  userOfferer: GetEducationalOffererResponseModel | null
  mode: Mode
  isOfferBooked?: boolean
  isOfferActive?: boolean
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
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
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

  const onSubmit = async (offerValues: OfferEducationalFormValues) => {
    let response = null

    try {
      if (isTemplate) {
        if (offer === undefined) {
          const payload = createCollectiveOfferTemplatePayload(
            offerValues,
            isCollectiveOaActive
          )

          response = await api.createCollectiveOfferTemplate(payload)
        } else {
          const payload = createPatchOfferTemplatePayload(
            offerValues,
            initialValues,
            isCollectiveOaActive
          )
          response = await api.editCollectiveOfferTemplate(offer.id, payload)
        }
      } else {
        if (offer === undefined) {
          const payload = createCollectiveOfferPayload(
            offerValues,
            isCollectiveOaActive
          )

          response = await api.createCollectiveOffer(payload)
        } else {
          const payload = createPatchOfferPayload(
            offerValues,
            initialValues,
            isCollectiveOaActive
          )
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
          offer.isTemplate
            ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
            : GET_COLLECTIVE_OFFER_QUERY_KEY,
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

        formik.setErrors(serializedError)
        notify.error(FORM_ERROR_MESSAGE)
      } else {
        notify.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema: getOfferEducationalValidationSchema(isCollectiveOaActive),
  })

  if (
    mode === Mode.CREATION &&
    formik.values.offererId !== selectedOffererId?.toString()
  ) {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    formik.setFieldValue('offererId', selectedOffererId?.toString())
  }

  return (
    <>
      {offer && (
        <OfferEducationalActions
          className={styles.actions}
          offer={offer}
          mode={mode}
        />
      )}
      <FormikProvider
        value={{
          ...formik,
          resetForm,
        }}
      >
        <form onSubmit={formik.handleSubmit}>
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
            isSubmitting={formik.isSubmitting}
            venues={venues}
          />
        </form>
      </FormikProvider>
      <RouteLeavingGuardCollectiveOfferCreation
        when={formik.dirty && !formik.isSubmitting}
      />
    </>
  )
}
