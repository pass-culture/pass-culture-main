import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalOfferType,
  extractInitialStockValues,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import patchCollectiveStockAdapter from 'pages/CollectiveOfferStockEdition/adapters/patchCollectiveStockAdapter'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

export const CollectiveOfferStockCreation = ({
  offer,
  setOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element | null => {
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')

  const [offerTemplate, setOfferTemplate] = useState<CollectiveOfferTemplate>()

  useEffect(() => {
    const fetchOfferTemplateDetails = async () => {
      if (!(isCollectiveOffer(offer) && offer.templateId)) {
        return null
      }
      const { isOk, payload, message } =
        await getCollectiveOfferTemplateAdapter(offer.templateId)
      if (!isOk) {
        return notify.error(message)
      }
      setOfferTemplate(payload)
    }
    fetchOfferTemplateDetails()
  }, [])

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      "Impossible de mettre à jour les stocks d'une offre vitrine."
    )
  }

  const initialValues = extractInitialStockValues(offer, offerTemplate)

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let createdOfferTemplateId: string | null = null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE
    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      createdOfferTemplateId = response.payload ? response.payload.id : null
    } else {
      const response = offer.collectiveStock
        ? await patchCollectiveStockAdapter({
            offer,
            stockId: offer.collectiveStock.nonHumanizedId,
            values,
            initialValues,
          })
        : await postCollectiveStockAdapter({
            offer,
            values,
          })
      isOk = response.isOk
      message = response.message

      if (offer && response.payload !== null) {
        setOffer({
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...response.payload,
            isBooked: false,
            isCancellable: offer.isCancellable,
          },
        })
      }
    }

    if (!isOk) {
      return notify.error(message)
    }

    let url = `/offre/${computeURLCollectiveOfferId(
      isTemplate && createdOfferTemplateId != null
        ? createdOfferTemplateId
        : offer.id,
      isTemplate
    )}/collectif`

    if (!isTemplate) {
      url = `${url}/visibilite`
    } else {
      url = `${url}/creation/recapitulatif`
    }
    navigate(url)
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer?.name}
      isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
      isTemplate={isTemplate}
      isCreation={isCreation}
    >
      <PageTitle title="Date et prix" />
      <OfferEducationalStockScreen
        initialValues={initialValues}
        mode={Mode.CREATION}
        offer={offer}
        onSubmit={handleSubmitStock}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </CollectiveOfferLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferStockCreation)
