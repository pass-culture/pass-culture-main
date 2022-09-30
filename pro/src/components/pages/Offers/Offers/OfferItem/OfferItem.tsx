import React from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'components/hooks/useOfferEditionURL'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'

import CheckboxCell from './Cells/CheckboxCell'
import EditOfferCell from './Cells/EditOfferCell'
import EditStocksCell from './Cells/EditStocksCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferRemainingStockCell from './Cells/OfferRemainingStockCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  audience: Audience
}

const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
}: OfferItemProps) => {
  const { venue, id, isEducational, isShowcase } = offer
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    id,
    isOfferFormV3,
    !!isShowcase
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    id,
    !!isShowcase
  )

  const isOfferEditable = offer ? offer.isEditable : null
  const isOfferInactiveOrExpiredOrDisabled =
    !offer.isActive ||
    offer.hasBookingLimitDatetimesPassed ||
    isOfferDisabled(offer.status)

  return (
    <tr
      className={`offer-item ${
        isOfferInactiveOrExpiredOrDisabled ? 'inactive' : ''
      } offer-row`}
    >
      <CheckboxCell
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />
      {audience === Audience.INDIVIDUAL && (
        <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      )}
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferVenueCell venue={venue} />
      {audience === Audience.INDIVIDUAL ? (
        <OfferRemainingStockCell stocks={offer.stocks} />
      ) : (
        <OfferInstitutionCell
          educationalInstitution={offer.educationalInstitution}
        />
      )}
      <OfferStatusCell status={offer.status} />
      <EditStocksCell editionStockLink={editionStockLink} />
      <EditOfferCell
        isOfferEditable={Boolean(isOfferEditable)}
        name={offer.name}
        editionOfferLink={editionOfferLink}
      />
    </tr>
  )
}

export default OfferItem
