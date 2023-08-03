import React from 'react'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { Mode } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import OfferEducationalScreen from 'screens/OfferEducational'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

const CollectiveOfferEdition = ({
  offer,
  setOffer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const isNationalSystemActive = useActiveFeature('WIP_ENABLE_NATIONAL_SYSTEM')
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOfferer.id ?? null,
    isNationalSystemActive,
    offer
  )

  if (!isReady || !offer) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
      <OfferEducationalScreen
        categories={offerEducationalFormData.categories}
        userOfferers={offerEducationalFormData.offerers}
        domainsOptions={offerEducationalFormData.domains}
        nationalPrograms={offerEducationalFormData.nationalPrograms}
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
