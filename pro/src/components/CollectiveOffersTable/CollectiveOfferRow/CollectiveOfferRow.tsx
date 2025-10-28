import classNames from 'classnames'

import {
  type CollectiveOfferBookableResponseModel,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { isCollectiveOfferBookable } from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { CheckboxCell } from '@/components/CollectiveOffersTable/CollectiveOfferRow/CheckboxCell'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import styles from './CollectiveOfferRow.module.scss'
import { CollectiveOfferStatusCell } from './CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { ExpirationCell } from './ExpirationCell/ExpirationCell'
import { OfferEventDateCell } from './OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from './OfferInstitutionCell/OfferInstitutionCell'
import { OfferLocationCell } from './OfferLocationCell/OfferLocationCell'
import { OfferNameCell } from './OfferNameCell/OfferNameCell'
import { PriceAndParticipantsCell } from './PriceAndParticipantsCell/PriceAndParticipantsCell'

export type CollectiveOfferRowProps<
  T extends
    | CollectiveOfferTemplateResponseModel
    | CollectiveOfferBookableResponseModel,
> = {
  isSelected: boolean
  offer: T
  selectOffer: (offer: T) => void
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  isFirstRow: boolean
}

function isCollectiveOfferPublishedOrPreBooked(
  offer:
    | CollectiveOfferBookableResponseModel
    | CollectiveOfferTemplateResponseModel
) {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED
  )
}

export const CollectiveOfferRow = <
  T extends
    | CollectiveOfferTemplateResponseModel
    | CollectiveOfferBookableResponseModel,
>({
  offer,
  isSelected,
  selectOffer,
  urlSearchFilters,
  isFirstRow,
}: CollectiveOfferRowProps<T>) => {
  const isTemplateTable = !isCollectiveOfferBookable(offer)
  const id = computeURLCollectiveOfferId(offer.id, isTemplateTable)

  const rowId = `collective-offer-${id}`

  const draftOfferLink =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${id}/creation`

  const offerLink = draftOfferLink || `/offre/${id}/collectif/recapitulatif`

  const editionOfferLink = draftOfferLink || `/offre/${id}/collectif/edition`

  const bookingLimitDate = isCollectiveOfferBookable(offer)
    ? offer.stock?.bookingLimitDatetime
    : null

  const hasExpirationRow =
    isCollectiveOfferBookable(offer) &&
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
        {isCollectiveOfferBookable(offer) && (
          <PriceAndParticipantsCell rowId={rowId} offer={offer} />
        )}
        {!isTemplateTable && (
          <OfferInstitutionCell
            rowId={rowId}
            educationalInstitution={offer.educationalInstitution}
            className={styles['collective-cell-institution']}
          />
        )}
        <OfferLocationCell rowId={rowId} offerLocation={offer.location} />
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
            className={styles['collective-cell-expiration']}
          />
        </tr>
      )}
    </>
  )
}
