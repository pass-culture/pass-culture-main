import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { isCollectiveOffer, Mode } from 'commons/core/OfferEducational/types'
import { useIsNewInterfaceActive } from 'commons/hooks/useIsNewInterfaceActive'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useOfferEducationalFormData'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { OfferEducational } from '../components/OfferEducational/OfferEducational'

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
          offer={offer}
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
