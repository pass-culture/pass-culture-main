import React from 'react'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  Mode,
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import OfferEducationalScreen from 'screens/OfferEducational'
import { withCollectiveOfferFromParams } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

const CollectiveOfferEdition = ({
  offer,
  setOffer,
  reloadCollectiveOffer,
  isTemplate,
}: {
  offer: CollectiveOffer | CollectiveOfferTemplate
  reloadCollectiveOffer: () => void
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  isTemplate: boolean
}): JSX.Element => {
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOffererId ?? null,
    offer
  )

  if (!isReady || !offer) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
      <PageTitle title="Détails de l'offre" />
      <OfferEducationalScreen
        categories={offerEducationalFormData.categories}
        userOfferers={offerEducationalFormData.offerers}
        domainsOptions={offerEducationalFormData.domains}
        offer={offer}
        setOffer={setOffer}
        isOfferActive={offer?.isActive}
        isOfferBooked={
          offer?.isTemplate ? false : offer?.collectiveStock?.isBooked
        }
        mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
        reloadCollectiveOffer={reloadCollectiveOffer}
        isTemplate={offer.isTemplate}
      />
    </CollectiveOfferLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferEdition)
