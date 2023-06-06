import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CanOffererCreateCollectiveOffer,
  IOfferEducationalFormValues,
  Mode,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  applyVenueDefaultsToFormValues,
} from 'core/OfferEducational'
import patchCollectiveOfferAdapter from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import postCollectiveOfferAdapter from 'core/OfferEducational/adapters/postCollectiveOfferAdapter'
import postCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateAdapter'
import { computeInitialValuesFromOffer } from 'core/OfferEducational/utils/computeInitialValuesFromOffer'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { patchCollectiveOfferTemplateAdapter } from 'pages/CollectiveOfferEdition/adapters/patchCollectiveOfferTemplateAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'

import styles from './OfferEducational.module.scss'
import OfferEducationalForm from './OfferEducationalForm'
import { useCollectiveOfferImageUpload } from './useCollectiveOfferImageUpload'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalProps {
  offer?: CollectiveOffer | CollectiveOfferTemplate
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  categories: EducationalCategories
  userOfferers: GetEducationalOffererResponseModel[]
  getIsOffererEligible?: CanOffererCreateCollectiveOffer
  mode: Mode
  isOfferBooked?: boolean
  isOfferActive?: boolean
  domainsOptions: SelectOption[]
  isTemplate: boolean
  isOfferCreated?: boolean
  reloadCollectiveOffer?: () => void
}

const OfferEducational = ({
  offer,
  setOffer,
  categories,
  userOfferers,
  domainsOptions,
  getIsOffererEligible,
  mode,
  isOfferBooked = false,
  isTemplate,
  reloadCollectiveOffer,
}: IOfferEducationalProps): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const {
    structure: offererId,
    lieu: venueId,
    requete: requestId,
  } = queryParamsFromOfferer(location)

  const baseInitialValues = computeInitialValuesFromOffer(
    categories,
    userOfferers,
    offer,
    offererId,
    venueId
  )
  const isOfferCreated = offer !== undefined
  const initialValues =
    mode === Mode.CREATION
      ? applyVenueDefaultsToFormValues(
          baseInitialValues,
          userOfferers,
          isOfferCreated,
          categories
        )
      : baseInitialValues

  const onSubmit = async (offerValues: IOfferEducationalFormValues) => {
    let response = null
    if (isTemplate) {
      if (offer === undefined) {
        response = postCollectiveOfferTemplateAdapter({ offer: offerValues })
      } else {
        response = await patchCollectiveOfferTemplateAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.nonHumanizedId,
        })
      }
    } else {
      if (offer === undefined) {
        response = postCollectiveOfferAdapter({ offer: offerValues })
      } else {
        response = await patchCollectiveOfferAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.nonHumanizedId,
        })
      }
    }

    const { payload, isOk, message } = await response
    if (!isOk) {
      return notify.error(message)
    }
    const offerId = offer?.id ?? payload.id
    await handleImageOnSubmit(offerId)
    if (
      offer &&
      (isCollectiveOffer(payload) || isCollectiveOfferTemplate(payload))
    ) {
      setOffer({
        ...payload,
        imageUrl: imageOffer?.url,
        imageCredit: imageOffer?.credit,
      })
    }
    if (mode === Mode.EDITION && offer !== undefined) {
      return navigate(
        `/offre/${computeURLCollectiveOfferId(
          offer.nonHumanizedId,
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
    validationSchema,
  })

  return (
    <>
      {offer && (
        <OfferEducationalActions
          className={styles.actions}
          isBooked={isOfferBooked}
          offer={offer}
          reloadCollectiveOffer={reloadCollectiveOffer}
          mode={mode}
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
            offer={offer}
          />
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducational
