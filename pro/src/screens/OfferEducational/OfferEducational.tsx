import { FormikProvider, useFormik } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import {
  GetEducationalOffererResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'config/swrQueryKeys'
import { patchCollectiveOfferAdapter } from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import { postCollectiveOfferAdapter } from 'core/OfferEducational/adapters/postCollectiveOfferAdapter'
import { postCollectiveOfferTemplateAdapter } from 'core/OfferEducational/adapters/postCollectiveOfferTemplateAdapter'
import {
  Mode,
  OfferEducationalFormValues,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from 'core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { computeInitialValuesFromOffer } from 'core/OfferEducational/utils/computeInitialValuesFromOffer'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { patchCollectiveOfferTemplateAdapter } from 'pages/CollectiveOfferEdition/adapters/patchCollectiveOfferTemplateAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'

import styles from './OfferEducational.module.scss'
import OfferEducationalForm from './OfferEducationalForm'
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
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

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
    if (isTemplate) {
      if (offer === undefined) {
        response = await postCollectiveOfferTemplateAdapter({
          offer: offerValues,
          isCustomContactActive,
        })
      } else {
        response = await patchCollectiveOfferTemplateAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.id,
          isCustomContactActive,
        })
      }
    } else {
      if (offer === undefined) {
        response = await postCollectiveOfferAdapter({
          offer: offerValues,
        })
      } else {
        response = await patchCollectiveOfferAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.id,
        })
      }
    }

    const { payload, isOk, message } = response
    if (!isOk) {
      return notify.error(message)
    }
    const offerId = offer?.id ?? payload.id
    await handleImageOnSubmit(offerId)
    if (
      offer &&
      (isCollectiveOffer(payload) || isCollectiveOfferTemplate(payload))
    ) {
      await mutate(
        offer.isTemplate
          ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
          : GET_COLLECTIVE_OFFER_QUERY_KEY,
        {
          ...payload,
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
        ? `/offre/${payload.id}/collectif/vitrine/creation/recapitulatif`
        : `/offre/${payload.id}/collectif/stocks${requestIdParams}`
    )
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema: getOfferEducationalValidationSchema(
      isCustomContactActive
    ),
  })

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
