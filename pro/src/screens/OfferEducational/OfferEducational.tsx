import { FormikProvider, useFormik } from 'formik'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  OfferEducationalFormValues,
} from 'core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from 'core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { computeInitialValuesFromOffer } from 'core/OfferEducational/utils/computeInitialValuesFromOffer'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from 'core/OfferEducational/utils/createOfferPayload'
import {
  FORM_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import {
  createPatchOfferPayload,
  createPatchOfferTemplatePayload,
} from 'pages/CollectiveOfferEdition/utils/createPatchOfferPayload'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { selectCurrentOffererId } from 'store/user/selectors'

import styles from './OfferEducational.module.scss'
import { OfferEducationalForm } from './OfferEducationalForm/OfferEducationalForm'
import { useCollectiveOfferImageUpload } from './useCollectiveOfferImageUpload'
import { getOfferEducationalValidationSchema } from './validationSchema'

export interface OfferEducationalProps {
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel

  userOfferers: GetEducationalOffererResponseModel[]
  mode: Mode
  isOfferBooked?: boolean
  isOfferActive?: boolean
  domainsOptions: SelectOption[]
  nationalPrograms: SelectOption<number>[]
  isTemplate: boolean
  isOfferCreated?: boolean
}

export const OfferEducational = ({
  offer,
  userOfferers,
  domainsOptions,
  nationalPrograms,
  mode,
  isOfferBooked = false,
  isTemplate,
}: OfferEducationalProps): JSX.Element => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const isCustomContactActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT'
  )
  const { mutate } = useSWRConfig()

  const {
    structure: offererId,
    lieu: venueId,
    requete: requestId,
  } = queryParamsFromOfferer(location)

  const baseInitialValues = computeInitialValuesFromOffer(
    userOfferers,
    isTemplate,
    offer,
    offererId,
    venueId,
    isMarseilleEnabled,
    isCustomContactActive
  )
  const isOfferCreated = offer !== undefined
  const initialValues =
    mode === Mode.CREATION
      ? applyVenueDefaultsToFormValues(
          baseInitialValues,
          userOfferers,
          isOfferCreated
        )
      : baseInitialValues

  const onSubmit = async (offerValues: OfferEducationalFormValues) => {
    let response = null

    try {
      if (isTemplate) {
        if (offer === undefined) {
          const payload = createCollectiveOfferTemplatePayload(
            offerValues,
            isCustomContactActive
          )

          response = await api.createCollectiveOfferTemplate(payload)
        } else {
          const payload = createPatchOfferTemplatePayload(
            offerValues,
            initialValues,
            isCustomContactActive
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
        notify.error(FORM_ERROR_MESSAGE)
      } else {
        notify.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema: getOfferEducationalValidationSchema(
      isCustomContactActive
    ),
  })

  if (
    isNewInterfaceActive &&
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
          isBooked={isOfferBooked}
          offer={offer}
          mode={mode}
        />
      )}
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}>
          <OfferEducationalForm
            mode={mode}
            userOfferers={userOfferers}
            domainsOptions={domainsOptions}
            nationalPrograms={nationalPrograms}
            isTemplate={isTemplate}
            imageOffer={imageOffer}
            onImageDelete={onImageDelete}
            onImageUpload={onImageUpload}
            isOfferCreated={isOfferCreated}
            offer={offer}
          />
        </form>
      </FormikProvider>
    </>
  )
}
