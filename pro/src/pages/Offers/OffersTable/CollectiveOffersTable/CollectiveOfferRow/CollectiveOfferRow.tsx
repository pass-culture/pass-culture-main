import classNames from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'

import { CheckboxCell } from '../../Cells/CheckboxCell'
import { CollectiveActionsCells } from '../../Cells/CollectiveActionsCells'
import { CollectiveOfferStatusCell } from '../../Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { OfferEventDateCell } from '../../Cells/OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from '../../Cells/OfferInstitutionCell'
import { OfferNameCell } from '../../Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from '../../Cells/OfferVenueCell'
import { ThumbCell } from '../../Cells/ThumbCell'
import styles from '../../OfferRow.module.scss'

export type CollectiveOfferRowProps = {
  isSelected: boolean
  offer: CollectiveOfferResponseModel
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  urlSearchFilters: SearchFiltersParams
}

export const CollectiveOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  urlSearchFilters,
}: CollectiveOfferRowProps) => {
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: true,
    offerId: offer.id,
    isShowcase: Boolean(offer.isShowcase),
  })

  const rowId = `collective-offer-${offer.isShowcase ? 'T-' : ''}${offer.id}`

  return (
    <>
      <tr
        className={classNames(styles['offer-item'], {
          [styles['inactive']]: isOfferDisabled(offer.status),
        })}
        data-testid="offer-item-row"
      >
        <th
          rowSpan={
            !isCollectiveOffersExpirationEnabled || offer.isShowcase ? 1 : 2
          }
          scope="rowgroup"
          className={styles['reference-row-head']}
          id={rowId}
        >
          <span className={'visually-hidden'}>{offer.name}</span>
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
      {isCollectiveOffersExpirationEnabled && !offer.isShowcase && (
        <tr>
          <td colSpan={1} />
          <td
            colSpan={8}
            style={{ backgroundColor: 'red' }}
            headers={`${rowId} collective-offer-head-expiration`}
          >
            Expire dans x jours
          </td>
        </tr>
      )}
    </>
  )
}
