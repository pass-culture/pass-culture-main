import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '../CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInformationForm } from './components/CollectiveOfferInformationForm/CollectiveOfferInformationForm'

// TODO (igabriele, 2026-07-02): Delete this useless intermediary component:
// 1. Move the layout inro @/layouts/
// 2. Create a `collectiveOfferRouteGroup` in `AppRouter/routes/` with the shared layout
// 3. Delete `<CollectiveOfferInformation>`
export const CollectiveOfferInformation = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const isEdition = location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isCreation={!isEdition}
      requestId={requestId}
      offer={offer}
    >
      <CollectiveOfferInformationForm offer={offer} />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferInformation
)
