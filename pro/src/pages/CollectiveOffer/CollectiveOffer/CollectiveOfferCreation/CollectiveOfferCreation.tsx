import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { isCollectiveOffer, Mode } from 'commons/core/OfferEducational/types'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { queryParamsFromOfferer } from 'commons/utils/queryParamsFromOfferer'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useOfferEducationalFormData'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { OfferEducational } from '../components/OfferEducational/OfferEducational'

export const CollectiveOfferCreation = ({
  offer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { requete: requestId } = queryParamsFromOfferer(location)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = selectedOffererId?.toString()
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    Number(offererId),
    offer
  )

  return (
    <Layout layout={'sticky-actions'}>
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
            userOfferer={offerEducationalFormData.offerer}
            domainsOptions={offerEducationalFormData.domains}
            nationalPrograms={offerEducationalFormData.nationalPrograms}
            offer={offer}
            mode={Mode.CREATION}
            isTemplate={isTemplate}
          />
        </CollectiveOfferLayout>
      )}
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withOptionalCollectiveOfferFromParams(
  CollectiveOfferCreation
)
