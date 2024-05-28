import React from 'react'

import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { isCollectiveOfferTemplate, Mode } from 'core/OfferEducational/types'
import { OfferEducational } from 'screens/OfferEducational/OfferEducational'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from 'screens/OfferEducational/useOfferEducationalFormData'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const CollectiveOfferEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOfferer.id,
    offer
  )

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  return (
    <AppLayout layout="sticky-actions">
      {!isReady ? (
        <Spinner />
      ) : (
        <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
          <OfferEducational
            userOfferers={offerEducationalFormData.offerers}
            domainsOptions={offerEducationalFormData.domains}
            nationalPrograms={offerEducationalFormData.nationalPrograms}
            offer={offer}
            isOfferActive={offer.isActive}
            isOfferBooked={
              isOfferTemplate ? false : offer.collectiveStock?.isBooked
            }
            mode={offer.isEditable ? Mode.EDITION : Mode.READ_ONLY}
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
