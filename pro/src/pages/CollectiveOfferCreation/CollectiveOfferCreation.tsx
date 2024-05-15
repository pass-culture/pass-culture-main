import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { isCollectiveOffer, Mode } from 'core/OfferEducational/types'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { OfferEducational } from 'screens/OfferEducational/OfferEducational'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

export const CollectiveOfferCreation = ({
  offer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { structure: offererId, requete: requestId } =
    queryParamsFromOfferer(location)
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    Number(offererId),
    offer
  )

  return (
    <AppLayout layout={'sticky-actions'}>
      {!isReady ? (
        <Spinner />
      ) : (
        <CollectiveOfferLayout
          subTitle={offer?.name}
          isCreation
          isTemplate={isTemplate}
          isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
          requestId={requestId}
        >
          <OfferEducational
            userOfferers={offerEducationalFormData.offerers}
            domainsOptions={offerEducationalFormData.domains}
            nationalPrograms={offerEducationalFormData.nationalPrograms}
            offer={offer}
            mode={Mode.CREATION}
            isTemplate={isTemplate}
          />
          <RouteLeavingGuardCollectiveOfferCreation />
        </CollectiveOfferLayout>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withOptionalCollectiveOfferFromParams(
  CollectiveOfferCreation
)
