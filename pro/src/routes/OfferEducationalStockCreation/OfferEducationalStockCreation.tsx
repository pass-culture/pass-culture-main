import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
  getStockCollectiveOfferAdapter,
} from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

const OfferEducationalStockCreation = (): JSX.Element => {
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()

  // FIX ME
  const handleSubmitStock = async (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let payload: { id: string } | null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE

    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    } else {
      const response = await postCollectiveStockAdapter({
        offer,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    }

    if (!isOk) {
      return notify.error(message)
    }

    let url = `/offre/${isTemplate ? 'T-' : ''}${
      isTemplate ? payload?.id : offer.id
    }/collectif`

    if (!isTemplate) {
      url = `${url}/visibilite`
    } else {
      url = `${url}/confirmation`
    }
    history.push(url)
  }

  useEffect(() => {
    if (!isReady) {
      const loadOffer = async () => {
        const { payload, message, isOk } = await getStockCollectiveOfferAdapter(
          offerId
        )

        if (!isOk) {
          return notify.error(message)
        }

        setOffer(payload)
        setIsReady(true)
      }

      loadOffer()
    }
  }, [offerId, notify, isReady])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.STOCKS}
      isCreatingOffer
      title="Créer une nouvelle offre collective"
    >
      {offer && isReady ? (
        <>
          <OfferEducationalStockScreen
            initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
            mode={Mode.CREATION}
            offer={offer}
            onSubmit={handleSubmitStock}
          />
          <RouteLeavingGuardOfferCreation isCollectiveFlow />
        </>
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalStockCreation
