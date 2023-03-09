import { useState, useCallback, useEffect, ComponentType } from 'react'
import { useParams } from 'react-router-dom-v5-compat'

import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  extractOfferIdAndOfferTypeFromRouteParams,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import Spinner from 'ui-kit/Spinner/Spinner'

export type MandatoryCollectiveOfferFromParamsProps = {
  offer: CollectiveOffer | CollectiveOfferTemplate
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  reloadCollectiveOffer: () => Promise<void>
  isTemplate: boolean
}

export type OptionalCollectiveOfferFromParamsProps = Omit<
  MandatoryCollectiveOfferFromParamsProps,
  'offer'
> &
  Partial<Pick<MandatoryCollectiveOfferFromParamsProps, 'offer'>>

export const useCollectiveOfferFromParams =
  (): OptionalCollectiveOfferFromParamsProps => {
    const { offerId: offerIdFromParams } = useParams<{
      offerId: string
    }>()

    if (offerIdFromParams === undefined) {
      throw new Error('useOffer hook called on a page without offerId')
    }

    const { offerId, isTemplate } =
      extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

    const [offer, setOffer] = useState<
      CollectiveOffer | CollectiveOfferTemplate
    >()

    const loadCollectiveOffer = useCallback(async () => {
      const adapter = isTemplate
        ? getCollectiveOfferTemplateAdapter
        : getCollectiveOfferAdapter
      const response = await adapter(offerId)
      if (response.isOk) {
        setOffer(response.payload)
      }
    }, [offerId])

    useEffect(() => {
      loadCollectiveOffer()
    }, [])

    return {
      offer,
      setOffer,
      reloadCollectiveOffer: loadCollectiveOffer,
      isTemplate,
    }
  }

export const withCollectiveOfferFromParams = <T,>(
  Component: ComponentType<T & OptionalCollectiveOfferFromParamsProps>,
  isOfferMandatory = true
) => {
  const CollectiveOfferWrapperComponent = (props: T) => {
    const additionalProps = useCollectiveOfferFromParams()

    if (isOfferMandatory && additionalProps.offer === undefined) {
      return <Spinner />
    }

    return <Component {...props} {...additionalProps} />
  }

  return CollectiveOfferWrapperComponent
}
