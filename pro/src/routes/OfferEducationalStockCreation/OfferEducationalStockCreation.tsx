import React, { useState, useEffect } from 'react'
import { useHistory } from 'react-router-dom'
import { useParams } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  getStockCollectiveOfferAdapter,
  getStockOfferAdapter,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'
import postEducationalShadowStockAdapter from './adapters/postEducationalShadowStock'
import postEducationalStockAdapter from './adapters/postEducationalStock'

const OfferEducationalStockCreation = (): JSX.Element => {
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()
  const isNewCollectiveModelEnabled = useActiveFeature(
    'ENABLE_NEW_COLLECTIVE_MODEL'
  )
  const enableIndividualAndCollectiveSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const handleSubmitStock = async (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let payload: {id: string} | null
    const isTemplate = values.educationalOfferType === EducationalOfferType.SHOWCASE

    if (isTemplate) {
      const adapter = isNewCollectiveModelEnabled
        ? postCollectiveOfferTemplateAdapter
        : postEducationalShadowStockAdapter
      const response = await adapter({
        offerId: enableIndividualAndCollectiveSeparation && !isNewCollectiveModelEnabled ? offer.offerId ?? '' : offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    } else {
      const adapter = isNewCollectiveModelEnabled
        ? postCollectiveStockAdapter
        : postEducationalStockAdapter
      const response = await adapter({
        offer,
        values,
        enableIndividualAndCollectiveSeparation,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    }


    if (!isOk) {
      return notify.error(message)
    }

    const successPayload = payload as unknown as {id: string}
    const shouldUseNewTemplateIds = isTemplate && enableIndividualAndCollectiveSeparation
    history.push(`/offre/${shouldUseNewTemplateIds ? 'T-' : ''}${shouldUseNewTemplateIds ? successPayload.id : offer.id}/collectif/confirmation`)
  }

  useEffect(() => {
    if (!isReady) {
      const loadOffer = async () => {
        const getOfferAdapter = enableIndividualAndCollectiveSeparation
          ? getStockCollectiveOfferAdapter
          : getStockOfferAdapter
        const { payload, message, isOk } = await getOfferAdapter(offerId)

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
      title="Créer une nouvelle offre scolaire"
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
