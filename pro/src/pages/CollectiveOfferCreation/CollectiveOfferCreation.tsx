import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { isCollectiveOffer, Mode } from 'core/OfferEducational/types'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { OfferEducational } from 'screens/OfferEducational/OfferEducational'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from 'screens/OfferEducational/useOfferEducationalFormData'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const CollectiveOfferCreation = ({
  offer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const location = useLocation()
  const { structure, requete: requestId } = queryParamsFromOfferer(location)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = isNewInterfaceActive
    ? selectedOffererId?.toString()
    : structure
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
