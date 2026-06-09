import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '../../CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInformationsForm } from '../components/CollectiveOfferInformationsForm/CollectiveOfferInformationsForm'

export const CollectiveOfferInformationsEdition = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  return (
    <CollectiveOfferLayout subTitle={offer.name} offer={offer}>
      <CollectiveOfferInformationsForm offer={offer} />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferInformationsEdition
)
