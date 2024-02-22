import React from 'react'

import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { Mode, isCollectiveOfferTemplate } from 'core/OfferEducational'
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
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOfferer.id ?? null,
    offer
  )

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  return (
    <AppLayout>
      {!isReady || !offer ? (
        <Spinner />
      ) : (
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
              offer && isOfferTemplate
                ? false
                : offer?.collectiveStock?.isBooked
            }
            mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
            reloadCollectiveOffer={reloadCollectiveOffer}
            isTemplate={isOfferTemplate}
          />
        </CollectiveOfferLayout>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(CollectiveOfferEdition)
