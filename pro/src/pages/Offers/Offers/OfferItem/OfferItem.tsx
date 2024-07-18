import cn from 'classnames'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'hooks/useOfferEditionURL'

import { CollectiveOfferItem } from './CollectiveOfferItem'
import { IndividualOfferItem } from './IndividualOfferItem'
import styles from './OfferItem.module.scss'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  selectOffer: (
    offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  ) => void
  audience: Audience
  urlSearchFilters: SearchFiltersParams
}

export const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
  urlSearchFilters,
}: OfferItemProps) => {
  const { venue, isEducational, isShowcase, status, id } = offer
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    id,
    !!isShowcase,
    status
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    id,
    !!isShowcase
  )

  return (
    <>
      {/* TODO the audience prop could probably be removed in the future */}
      {/* as it is redundant with the offer.isEducational property */}
      {audience === Audience.INDIVIDUAL && !isOfferEducational(offer) && (
        <tr
          className={cn(styles['offer-item'], {
            [styles['inactive']]: disabled,
          })}
          data-testid="offer-item-row"
        >
          <IndividualOfferItem
            disabled={disabled}
            offer={offer}
            isSelected={isSelected}
            selectOffer={selectOffer}
            editionOfferLink={editionOfferLink}
            editionStockLink={editionStockLink}
            venue={venue}
            audience={audience}
          />
        </tr>
      )}
      {audience === Audience.COLLECTIVE && isOfferEducational(offer) && (
        <>
          <tr
            className={cn(styles['offer-item'], {
              [styles['inactive']]: disabled,
            })}
            data-testid="offer-item-row"
          >
            <th
              scope="rowgroup"
              rowSpan={2}
              id={`collective-th-offer-${offer.id}`}
            >
              <span className="visually-hidden">{offer.name}</span>
            </th>
            <CollectiveOfferItem
              disabled={disabled}
              offer={offer}
              isSelected={isSelected}
              selectOffer={selectOffer}
              editionOfferLink={editionOfferLink}
              venue={venue}
              audience={audience}
              urlSearchFilters={urlSearchFilters}
            />
          </tr>
          <tr>
            <td colSpan={2} />
            <td
              className={styles['test-colspan']}
              colSpan={6}
              headers={`collective-th-offer-${offer.id} collective-th-expiration-date`}
            >
              {offer.id}
            </td>
          </tr>
        </>
      )}
    </>
  )
}
