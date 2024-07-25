import { Link } from 'react-router-dom'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'
import { Thumb } from 'ui-kit/Thumb/Thumb'

import styles from './Cells.module.scss'

export const ThumbCell = ({
  offer,
  editionOfferLink,
  headers,
}: {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  editionOfferLink: string
  headers?: string
}) => {
  return (
    <td className={styles['thumb-column']} headers={headers}>
      <Link
        className={styles['thumb-column-link']}
        title={`${offer.name} - éditer l’offre`}
        to={editionOfferLink}
      >
        <Thumb
          url={isOfferEducational(offer) ? offer.imageUrl : offer.thumbUrl}
          className={styles['offer-thumb']}
        />
      </Link>
    </td>
  )
}
