import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import getCollectiveOfferFormDataAdapter from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import patchCollectiveOfferAdapter from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import postCollectiveOfferAdapter from 'core/OfferEducational/adapters/postCollectiveOfferAdapter'
import postCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateAdapter'
import useNotification from 'hooks/useNotification'
import { patchCollectiveOfferTemplateAdapter } from 'pages/CollectiveOfferEdition/adapters/patchCollectiveOfferTemplateAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

import { useCollectiveOfferImageUpload } from './useCollectiveOfferImageUpload'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

interface CollectiveOfferCreationProps {
  offer?: CollectiveOffer | CollectiveOfferTemplate
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  isTemplate?: boolean
}

const CollectiveOfferCreation = ({
  offer,
  setOffer,
  isTemplate = false,
}: CollectiveOfferCreationProps): JSX.Element => {
  const history = useHistory()
  const location = useLocation()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, isTemplate)

  const handleSubmit = async (offerValues: IOfferEducationalFormValues) => {
    let response = null
    if (isTemplate) {
      if (offer === undefined) {
        response = postCollectiveOfferTemplateAdapter({ offer: offerValues })
      } else {
        response = await patchCollectiveOfferTemplateAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.id,
        })
      }
    } else {
      if (offer === undefined) {
        response = postCollectiveOfferAdapter({ offer: offerValues })
      } else {
        response = await patchCollectiveOfferAdapter({
          offer: offerValues,
          initialValues,
          offerId: offer.id,
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

    history.push(
      isTemplate
        ? `/offre/${payload.id}/collectif/vitrine/creation/recapitulatif`
        : `/offre/${payload.id}/collectif/stocks`
    )
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const result = await getCollectiveOfferFormDataAdapter({
          offererId,
          offer,
        })

        if (!result.isOk) {
          notify.error(result.message)
        }

        const { categories, offerers, domains, initialValues } = result.payload

        setScreenProps({
          categories: categories,
          userOfferers: offerers,
          domainsOptions: domains,
        })

        setInitialValues(values =>
          setInitialFormValues(
            { ...values, ...initialValues },
            offerers,
            initialValues.offererId ?? offererId,
            initialValues.venueId ?? venueId
          )
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return isReady && screenProps ? (
    <>
      <OfferEducationalScreen
        {...screenProps}
        getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
        initialValues={initialValues}
        mode={Mode.CREATION}
        onSubmit={handleSubmit}
        isTemplate={isTemplate}
        imageOffer={imageOffer}
        onImageDelete={onImageDelete}
        onImageUpload={onImageUpload}
        isOfferCreated={offer !== undefined}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </>
  ) : (
    <Spinner />
  )
}

export default CollectiveOfferCreation
