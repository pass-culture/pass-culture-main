import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import useGetStockCollectiveOfferAdapter from 'core/OfferEducational/adapters/useGetStockCollectiveOfferAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

const OfferEducationalStockCreation = (): JSX.Element | null => {
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

  const { isLoading, error, data } = useGetStockCollectiveOfferAdapter(offerId)

  if (error) {
    notify.error(error.message)
    return null
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.STOCKS,
        isCreatingOffer: true,
      }}
      title="Créer une nouvelle offre collective"
    >
      {!isLoading ? (
        <>
          <OfferEducationalStockScreen
            initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
            mode={Mode.CREATION}
            offer={data}
            onSubmit={handleSubmitStock}
          />
          <RouteLeavingGuardOfferCreation isCollectiveFlow />
        </>
      ) : (
        <Spinner />
      )}
    </CollectiveOfferLayout>
  )
}

export default OfferEducationalStockCreation
