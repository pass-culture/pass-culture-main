import React from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import { Offer, Venue } from 'core/Offers/types'

import CheckboxCell from './Cells/CheckboxCell'
import DuplicateOfferCell from './Cells/DuplicateOfferCell'
import EditOfferCell from './Cells/EditOfferCell'
import EditStocksCell from './Cells/EditStocksCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'

export type CollectiveOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  editionStockLink: string
  venue: Venue
  isOfferEditable: boolean
}

const CollectiveOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  editionStockLink,
  venue,
  isOfferEditable,
}: CollectiveOfferItemProps) => {
  const isCollectiveOfferDuplicationActive = useActiveFeature(
    'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE'
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
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferVenueCell venue={venue} />
      <OfferInstitutionCell
        educationalInstitution={offer.educationalInstitution}
      />
      <OfferStatusCell status={offer.status} />
      {isCollectiveOfferDuplicationActive ? (
        <DuplicateOfferCell isTemplate={Boolean(offer.isShowcase)} />
      ) : (
        <EditStocksCell editionStockLink={editionStockLink} />
      )}
      <EditOfferCell
        isOfferEditable={isOfferEditable}
        name={offer.name}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}

export default CollectiveOfferItem
