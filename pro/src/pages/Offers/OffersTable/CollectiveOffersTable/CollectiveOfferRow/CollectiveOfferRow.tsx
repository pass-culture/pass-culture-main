import classNames from 'classnames'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'

import { CheckboxCell } from '../../Cells/CheckboxCell'
import { CollectiveActionsCells } from '../../Cells/CollectiveActionsCells'
import { CollectiveOfferStatusCell } from '../../Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { ExpirationCell } from '../../Cells/ExpirationCell/ExpirationCell'
import { OfferEventDateCell } from '../../Cells/OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from '../../Cells/OfferInstitutionCell'
import { OfferNameCell } from '../../Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from '../../Cells/OfferVenueCell'
import { ThumbCell } from '../../Cells/ThumbCell'

import styles from './CollectiveOfferRow.module.scss'

export type CollectiveOfferRowProps = {
  isSelected: boolean
  offer: CollectiveOfferResponseModel
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  urlSearchFilters: SearchFiltersParams
  isFirstRow: boolean
}

function isCollectiveOfferActiveOrPreBooked(
  offer: CollectiveOfferResponseModel
) {
  return (
    offer.status === CollectiveOfferStatus.ACTIVE ||
    (offer.status === CollectiveOfferStatus.SOLD_OUT &&
      offer.booking?.booking_status === 'PENDING')
  )
}

export const CollectiveOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  urlSearchFilters,
  isFirstRow,
}: CollectiveOfferRowProps) => {
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: true,
    offerId: offer.id,
    status: offer.status,
    isShowcase: Boolean(offer.isShowcase),
  })

  const rowId = `collective-offer-${offer.isShowcase ? 'T-' : ''}${offer.id}`

  const bookingLimitDate = offer.stocks[0]?.bookingLimitDatetime

  const hasExpirationRow =
    isCollectiveOffersExpirationEnabled &&
    !offer.isShowcase &&
    isCollectiveOfferActiveOrPreBooked(offer) &&
    bookingLimitDate

  return (
    <>
      <tr
        className={classNames(styles['collective-row'], {
          [styles['collective-row-with-expiration']]: hasExpirationRow,
          [styles['is-first-row']]: isFirstRow,
        })}
        data-testid="offer-item-row"
      >
        <th
          rowSpan={hasExpirationRow ? 2 : 1}
          scope="rowgroup"
          className={styles['reference-row-head']}
          id={rowId}
        >
          <span className="visually-hidden">{offer.name}</span>
        </th>
        <CheckboxCell
          offerName={offer.name}
          isSelected={isSelected}
          disabled={isOfferDisabled(offer.status)}
          selectOffer={() => selectOffer(offer)}
          headers={`${rowId} collective-offer-head-checkbox`}
        />
        {isCollectiveOffersExpirationEnabled && (
          <td className={styles['expiration-date-cell']} />
        )}
        <ThumbCell
          offer={offer}
          editionOfferLink={editionOfferLink}
          inactive={isOfferDisabled(offer.status)}
          headers={`${rowId} collective-offer-head-image`}
        />

        <OfferNameCell
          offer={offer}
          editionOfferLink={editionOfferLink}
          headers={`${rowId} collective-offer-head-name`}
        />

        {isCollectiveOffersExpirationEnabled && (
          <OfferEventDateCell
            offer={offer}
            headers={`${rowId} collective-offer-head-expiration-date`}
          />
        )}

        <OfferVenueCell
          venue={offer.venue}
          headers={`${rowId} collective-offer-head-venue`}
        />

        <OfferInstitutionCell
          educationalInstitution={offer.educationalInstitution}
          headers={`${rowId} collective-offer-head-institution`}
        />

        <CollectiveOfferStatusCell
          offer={offer}
          headers={`${rowId} collective-offer-head-status`}
        />

        <CollectiveActionsCells
          offer={offer}
          editionOfferLink={editionOfferLink}
          urlSearchFilters={urlSearchFilters}
          isSelected={isSelected}
          deselectOffer={() => selectOffer(offer)}
          headers={`${rowId} collective-offer-head-actions`}
        />
      </tr>
      {hasExpirationRow && (
        <tr className={styles['collective-row']}>
          <td colSpan={1} />
          <ExpirationCell
            offer={offer}
            bookingLimitDate={bookingLimitDate}
            headers={`${rowId} collective-offer-head-expiration`}
          />
        </tr>
      )}
    </>
  )
}
