import classNames from 'classnames'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { CheckboxCell } from '@/components/OffersTable/Cells/CheckboxCell'
import { OfferVenueCell } from '@/components/OffersTable/Cells/OfferVenueCell'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import styles from './CollectiveOfferRow.module.scss'
import { CollectiveOfferStatusCell } from './CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { ExpirationCell } from './ExpirationCell/ExpirationCell'
import { OfferEventDateCell } from './OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from './OfferInstitutionCell/OfferInstitutionCell'
import { OfferNameCell } from './OfferNameCell/OfferNameCell'

export type CollectiveOfferRowProps = {
  isSelected: boolean
  offer: CollectiveOfferResponseModel
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  isFirstRow: boolean
}

function isCollectiveOfferPublishedOrPreBooked(
  offer: CollectiveOfferResponseModel
) {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED
  )
}

export const CollectiveOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  urlSearchFilters,
  isFirstRow,
}: CollectiveOfferRowProps) => {
  const id = computeURLCollectiveOfferId(offer.id, Boolean(offer.isShowcase))
  const isNewCollectiveOfferDetailPageActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE'
  )

  const rowId = `collective-offer-${id}`

  const isOfferDraft =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${id}/creation`

  const offerLink =
    isNewCollectiveOfferDetailPageActive && !offer.isShowcase
      ? `/offre/${id}/collectif/recapitulatif`
      : isOfferDraft || `/offre/${id}/collectif/recapitulatif`

  const editionOfferLink = isOfferDraft || `/offre/${id}/collectif/edition`

  const bookingLimitDate = offer.stocks[0]?.bookingLimitDatetime

  const hasExpirationRow =
    !offer.isShowcase &&
    isCollectiveOfferPublishedOrPreBooked(offer) &&
    !!bookingLimitDate

  const isSelectable = isCollectiveOfferSelectable(offer)

  return (
    <>
      <tr
        className={classNames(styles['collective-row'], {
          [styles['collective-row-with-expiration']]: hasExpirationRow,
          [styles['is-first-row']]: isFirstRow,
        })}
        data-testid="offer-item-row"
      >
        <CheckboxCell
          rowId={rowId}
          offerName={offer.name}
          isSelected={isSelected}
          disabled={!isSelectable}
          selectOffer={() => selectOffer(offer)}
          className={styles['collective-cell-checkbox']}
        />
        <td className={styles['expiration-date-cell']} />
        <OfferNameCell
          rowId={rowId}
          offer={offer}
          offerLink={offerLink}
          className={styles['collective-cell-name']}
          displayThumb={true}
        />
        <OfferEventDateCell
          rowId={rowId}
          offer={offer}
          className={styles['collective-cell-event-date']}
        />
        <OfferVenueCell
          rowId={rowId}
          venue={offer.venue}
          className={styles['collective-cell-venue']}
        />
        <OfferInstitutionCell
          rowId={rowId}
          educationalInstitution={offer.educationalInstitution}
          className={styles['collective-cell-institution']}
        />
        <CollectiveOfferStatusCell
          rowId={rowId}
          offer={offer}
          className={styles['collective-cell-status']}
        />
        <CollectiveActionsCells
          rowId={rowId}
          offer={offer}
          editionOfferLink={editionOfferLink}
          urlSearchFilters={urlSearchFilters}
          isSelected={isSelected}
          deselectOffer={() => selectOffer(offer)}
          className={styles['collective-cell-actions']}
        />
      </tr>
      {hasExpirationRow && (
        <tr className={styles['collective-row']}>
          <td colSpan={1} />
          <ExpirationCell
            rowId={rowId}
            offer={offer}
            bookingLimitDate={bookingLimitDate}
            className={styles['collective-cell-expiration']}
          />
        </tr>
      )}
    </>
  )
}
