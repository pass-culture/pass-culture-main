import classNames from 'classnames'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { CheckboxCell } from 'components/OffersTable/Cells/CheckboxCell'
import { OfferNameCell } from 'components/OffersTable/Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from 'components/OffersTable/Cells/OfferVenueCell'
import { ThumbCell } from 'components/OffersTable/Cells/ThumbCell'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import styles from './CollectiveOfferRow.module.scss'
import { CollectiveOfferStatusCell } from './CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { ExpirationBanner } from './ExpirationBanner/ExpirationBanner'
import { OfferEventDateCell } from './OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from './OfferInstitutionCell/OfferInstitutionCell'

export type CollectiveOfferRowProps = {
  isSelected: boolean
  offer: CollectiveOfferResponseModel
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  urlSearchFilters: CollectiveSearchFiltersParams
  isFirstRow: boolean
}

function isCollectiveOfferActiveOrPreBooked(
  offer: CollectiveOfferResponseModel
) {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.ACTIVE ||
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
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )

  const id = computeURLCollectiveOfferId(offer.id, Boolean(offer.isShowcase))

  const isOfferDraft =
    offer.status === CollectiveOfferStatus.DRAFT &&
    `/offre/collectif/${id}/creation`

  const offerLink = isOfferDraft || `/offre/${id}/collectif/recapitulatif`

  const editionOfferLink = isOfferDraft || `/offre/${id}/collectif/edition`

  const bookingLimitDate = offer.stocks[0]?.bookingLimitDatetime

  const hasExpirationRow =
    isCollectiveOffersExpirationEnabled &&
    !offer.isShowcase &&
    isCollectiveOfferActiveOrPreBooked(offer) &&
    !!bookingLimitDate

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
          offerName={offer.name}
          isSelected={isSelected}
          disabled={!offer.isEditable}
          selectOffer={() => selectOffer(offer)}
          className={styles['collective-cell-checkbox']}
        />
        <ThumbCell
          offer={offer}
          offerLink={offerLink}
          inactive={!offer.isEditable}
          className={styles['collective-cell-thumb']}
        />

        <OfferNameCell
          offer={offer}
          offerLink={offerLink}
          className={styles['collective-cell-name']}
        />

        {isCollectiveOffersExpirationEnabled && (
          <OfferEventDateCell
            offer={offer}
            className={styles['collective-cell-expiration-date']}
          />
        )}

        <OfferVenueCell
          venue={offer.venue}
          className={styles['collective-cell-venue']}
        />

        <OfferInstitutionCell
          educationalInstitution={offer.educationalInstitution}
          className={styles['collective-cell-institution']}
        />

        <CollectiveOfferStatusCell
          offer={offer}
          className={styles['collective-cell-status']}
          hasExpirationRow={hasExpirationRow}
          bookingLimitDate={bookingLimitDate}
        />

        <CollectiveActionsCells
          offer={offer}
          editionOfferLink={editionOfferLink}
          urlSearchFilters={urlSearchFilters}
          isSelected={isSelected}
          deselectOffer={() => selectOffer(offer)}
          className={styles['collective-cell-actions']}
        />
      </tr>
      {hasExpirationRow && (
        <tr className={styles['collective-row']} aria-hidden={true}>
          <td colSpan={1} />
          <td colSpan={8} className={classNames(styles['expiration-cell'])}>
            <ExpirationBanner
              offer={offer}
              bookingLimitDate={bookingLimitDate}
            />
          </td>
        </tr>
      )}
    </>
  )
}
