import { ComponentType } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
} from 'config/swrQueryKeys'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational/utils/extractOfferIdAndOfferTypeFromRouteParams'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export type MandatoryCollectiveOfferFromParamsProps = {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  isTemplate: boolean
  offerer: GetOffererResponseModel | undefined
}

export type OptionalCollectiveOfferFromParamsProps = Omit<
  MandatoryCollectiveOfferFromParamsProps,
  'offer' | 'offerer'
> &
  Partial<Pick<MandatoryCollectiveOfferFromParamsProps, 'offer' | 'offerer'>>

export const useCollectiveOfferFromParams = (
  isOfferMandatory: boolean,
  offerIdFromParams?: string
) => {
  const location = useLocation()
  const pathNameIncludesTemplate = location.pathname.includes('vitrine')

  const { offerId, isTemplateId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const isTemplate = isTemplateId || pathNameIncludesTemplate

  const { data: offer } = useSWR(
    offerId !== undefined
      ? [
          isTemplate
            ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
            : GET_COLLECTIVE_OFFER_QUERY_KEY,
          offerId,
        ]
      : null,
    ([, offerIdParams]) =>
      isTemplate
        ? api.getCollectiveOfferTemplate(offerIdParams)
        : api.getCollectiveOffer(offerIdParams)
  )

  const offererId = offer?.venue.managingOfferer.id
  const { data: offerer } = useSWR(
    offererId ? [GET_OFFERER_QUERY_KEY, offererId] : null,
    ([, offererIdParam]) => api.getOfferer(offererIdParam)
  )

  if (offerIdFromParams === undefined) {
    if (isOfferMandatory) {
      throw new Error('useOffer hook called on a page without offerId')
    } else {
      return {
        offer: undefined,
        isTemplate: pathNameIncludesTemplate,
        offerer: undefined,
      }
    }
  }

  return {
    offer,
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
