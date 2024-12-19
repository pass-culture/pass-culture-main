import classNames from 'classnames'
import { Link } from 'react-router-dom'

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
  inactive,
  className,
}: {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  offerLink: string
  inactive?: boolean
  className?: string
}) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['thumb-column']
      )}
    >
      <Link title={`${offer.name} - éditer l’offre`} to={offerLink}>
        <Thumb
          url={isOfferEducational(offer) ? offer.imageUrl : offer.thumbUrl}
          className={classNames(
            {
              [styles['thumb-column-inactive']]: inactive,
            },
            className
          )}
        />
      </Link>
    </td>
  )
}
