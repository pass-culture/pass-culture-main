import classNames from 'classnames'
import { Link } from 'react-router'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import styles from 'styles/components/Cells.module.scss'
import { Thumb } from 'ui-kit/Thumb/Thumb'

export const ThumbCell = ({
  offer,
  offerLink,
  inactive,
  className,
}: {
  offer: CollectiveOfferResponseModel
  offerLink: string
  rowId: string
  inactive?: boolean
  className?: string
}) => {
  return (
    <Link to={offerLink}>
      <Thumb
        alt={`${offer.name} - éditer l’offre`}
        url={offer.imageUrl}
        className={classNames(
          {
            [styles['thumb-column-inactive']]: inactive,
          },
          className
        )}
      />
    </Link>
  )
}
