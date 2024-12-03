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
  editionOfferLink,
  headers,
  inactive,
}: {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  editionOfferLink: string
  headers?: string
  inactive?: boolean
}) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['thumb-column']
      )}
      headers={headers}
    >
      <Link
        className={styles['thumb-column-link']}
        title={`${offer.name} - éditer l’offre`}
        to={editionOfferLink}
      >
        <Thumb
          url={isOfferEducational(offer) ? offer.imageUrl : offer.thumbUrl}
          className={classNames(styles['offer-thumb'], {
            [styles['thumb-inactive']]: inactive,
          })}
        />
      </Link>
    </td>
  )
}
