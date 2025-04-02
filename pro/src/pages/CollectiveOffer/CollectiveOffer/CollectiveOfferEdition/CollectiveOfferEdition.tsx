import { Layout } from 'app/App/layout/Layout'
import {
  isCollectiveOfferTemplate,
  Mode,
} from 'commons/core/OfferEducational/types'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { OfferEducational } from '../components/OfferEducational/OfferEducational'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '../components/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from '../components/OfferEducational/useOfferEducationalFormData'

const CollectiveOfferEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOfferer.id,
    offer
  )

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  if (!isReady) {
    return (
      <Layout layout={'sticky-actions'}>
        <Spinner />
      </Layout>
    )
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={isTemplate}
      offer={offer}
    >
      <OfferEducational
        userOfferer={offerEducationalFormData.offerer}
        domainsOptions={offerEducationalFormData.domains}
        venues={offerEducationalFormData.venues}
        offer={offer}
        isOfferActive={offer.isActive}
        isOfferBooked={
          isOfferTemplate ? false : offer.collectiveStock?.isBooked
        }
        mode={offer.isEditable ? Mode.EDITION : Mode.READ_ONLY}
        isTemplate={isOfferTemplate}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(CollectiveOfferEdition)
