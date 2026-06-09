import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '../../CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInformationsForm } from '../components/CollectiveOfferInformationsForm/CollectiveOfferInformationsForm'

export const CollectiveOfferInformationsCreation = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { requete: requestId } = queryParamsFromOfferer(location)
  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isCreation
      requestId={requestId}
      offer={offer}
    >
      <CollectiveOfferInformationsForm offer={offer} />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferInformationsCreation
)
