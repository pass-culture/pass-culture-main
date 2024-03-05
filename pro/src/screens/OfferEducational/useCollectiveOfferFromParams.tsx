import { ComponentType, useCallback, useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useActiveFeature from 'hooks/useActiveFeature'
import Spinner from 'ui-kit/Spinner/Spinner'

export type MandatoryCollectiveOfferFromParamsProps = {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  setOffer: (
    offer:
      | GetCollectiveOfferResponseModel
      | GetCollectiveOfferTemplateResponseModel
  ) => void
  reloadCollectiveOffer: () => Promise<void>
  isTemplate: boolean
  offerer: GetOffererResponseModel | undefined
}

export type OptionalCollectiveOfferFromParamsProps = Omit<
  MandatoryCollectiveOfferFromParamsProps,
  'offer' | 'offerer'
> &
  Partial<Pick<MandatoryCollectiveOfferFromParamsProps, 'offer' | 'offerer'>>

const useCollectiveOfferFromParams = (
  isOfferMandatory: boolean,
  offerIdFromParams?: string
) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const location = useLocation()
  const pathNameIncludesTemplate = location.pathname.includes('vitrine')

  const [offer, setOffer] = useState<
    GetCollectiveOfferResponseModel | GetCollectiveOfferTemplateResponseModel
  >()

  const [offerer, setOfferer] = useState<GetOffererResponseModel>()

  const { offerId, isTemplateId } = extractOfferIdAndOfferTypeFromRouteParams(
    offerIdFromParams || ''
  )

  const isTemplate = isTemplateId || pathNameIncludesTemplate

  const loadCollectiveOffer = useCallback(async () => {
    const adapter = isTemplate
      ? getCollectiveOfferTemplateAdapter
      : getCollectiveOfferAdapter
    const response = await adapter(offerId)
    if (response.isOk) {
      setOffer(response.payload)
      if (isNewBankDetailsJourneyEnabled) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        loadOfferer(response.payload.venue.managingOfferer.id)
      }
    }
  }, [offerId, isTemplate])

  async function loadOfferer(id: number) {
    const offererResponseModel = await api.getOfferer(id)
    setOfferer(offererResponseModel)
  }

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadCollectiveOffer()
  }, [])

  if (offerIdFromParams === undefined) {
    if (isOfferMandatory) {
      throw new Error('useOffer hook called on a page without offerId')
    } else {
      return {
        offer: undefined,
        setOffer: () => {},
        reloadCollectiveOffer: () => Promise.resolve(),
        isTemplate: false || pathNameIncludesTemplate,
        offerer: undefined,
      }
    }
  }

  return {
    offer,
    setOffer,
    reloadCollectiveOffer: loadCollectiveOffer,
    isTemplate,
    offerer,
  }
}

// Could be refactored with a react-router-v6 loader function
export const withCollectiveOfferFromParams = <T,>(
  Component: ComponentType<T & MandatoryCollectiveOfferFromParamsProps>
) => {
  const CollectiveOfferWrapperComponent = (props: T) => {
    const { offerId: offerIdFromParams } = useParams<{
      offerId: string
    }>()
    const additionalProps = useCollectiveOfferFromParams(
      true,
      offerIdFromParams
    )

    if (additionalProps.offer === undefined) {
      return <Spinner />
    }

    return (
      <Component
        {...props}
        {...additionalProps}
        offer={additionalProps.offer}
      />
    )
  }

  return CollectiveOfferWrapperComponent
}

export const withOptionalCollectiveOfferFromParams = <T,>(
  Component: ComponentType<T & OptionalCollectiveOfferFromParamsProps>
) => {
  const CollectiveOfferWrapperComponent = (props: T) => {
    const { offerId: offerIdFromParams } = useParams<{
      offerId: string
    }>()
    const additionalProps = useCollectiveOfferFromParams(
      false,
      offerIdFromParams
    )

    if (offerIdFromParams && additionalProps.offer === undefined) {
      return <Spinner />
    }

    return <Component {...props} {...additionalProps} />
  }

  return CollectiveOfferWrapperComponent
}
