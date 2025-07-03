import classNames from 'classnames'
import { Link } from 'react-router'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'commons/core/OfferEducational/types'
import styles from 'styles/components/Cells.module.scss'
import { Thumb } from 'ui-kit/Thumb/Thumb'

export const ThumbCell = ({
  offer,
  offerLink,
  rowId,
  inactive,
  className,
}: {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  offerLink: string
  rowId: string
  inactive?: boolean
  className?: string
}) => {
  return (
    <div
      role="cell"
      className={classNames(styles['offers-table-cell'])}
      // headers={`${rowId} ${getCellsDefinition().THUMB.id}`}
    >
      <Link to={offerLink}>
        <Thumb
          alt={`${offer.name} - éditer l’offre`}
          url={isOfferEducational(offer) ? offer.imageUrl : offer.thumbUrl}
          className={classNames(
            {
              [styles['thumb-column-inactive']]: inactive,
            },
            className
          )}
        />
      </Link>
    </div>
  )
}
