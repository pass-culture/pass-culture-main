import { Link } from 'react-router-dom'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'
import { Thumb } from 'ui-kit/Thumb/Thumb'

import styles from '../OfferItem.module.scss'

export const ThumbCell = ({
  offer,
  editionOfferLink,
}: {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  editionOfferLink: string
}) => {
  return (
    <td className={styles['thumb-column']}>
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
