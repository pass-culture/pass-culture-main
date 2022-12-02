import React from 'react'

import { Offer, Venue } from 'core/Offers/types'
import useActiveFeature from 'hooks/useActiveFeature'

import CheckboxCell from './Cells/CheckboxCell'
import CollectiveOfferStatusCell from './Cells/CollectiveOfferStatusCell'
import DuplicateOfferCell from './Cells/DuplicateOfferCell'
import EditOfferCell from './Cells/EditOfferCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

export type CollectiveOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  venue: Venue
  isOfferEditable: boolean
}

const CollectiveOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  venue,
  isOfferEditable,
}: CollectiveOfferItemProps) => {
  const isImageCollectiveOfferActive = useActiveFeature(
    'WIP_IMAGE_COLLECTIVE_OFFER'
  )
  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )
  return (
    <>
      <CheckboxCell
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />
      {isImageCollectiveOfferActive && (
        <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      )}
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferVenueCell venue={venue} />
      <OfferInstitutionCell
        educationalInstitution={offer.educationalInstitution}
      />
      {isImproveCollectiveStatusActive ? (
        <CollectiveOfferStatusCell offer={offer} />
      ) : (
        <OfferStatusCell status={offer.status} />
      )}
      <DuplicateOfferCell
        isTemplate={Boolean(offer.isShowcase)}
        templateOfferId={offer.id}
      />
      <EditOfferCell
        offer={offer}
        isOfferEditable={isOfferEditable}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}

export default CollectiveOfferItem
