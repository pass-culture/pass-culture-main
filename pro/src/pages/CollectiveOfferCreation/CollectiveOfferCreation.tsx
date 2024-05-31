import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { GET_EDUCATIONAL_OFFERERS_QUERY_KEY } from 'config/swrQueryKeys'
import { isCollectiveOffer, Mode } from 'core/OfferEducational/types'
import { getUserOfferersFromOffer } from 'core/OfferEducational/utils/getUserOfferersFromOffer'
import { serializeEducationalOfferers } from 'core/OfferEducational/utils/serializeEducationalOfferers'
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

  const { data, isLoading } = useSWR(
    [GET_EDUCATIONAL_OFFERERS_QUERY_KEY, offererId],
    ([, targetOffererId]) =>
      api.listEducationalOfferers(Number(targetOffererId))
  )
  const offerers = getUserOfferersFromOffer(
    serializeEducationalOfferers(data?.educationalOfferers || [])
  )

  return (
    <AppLayout layout={'sticky-actions'}>
      {!isReady || isLoading ? (
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
            userOfferers={offerers}
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
