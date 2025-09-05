import classNames from 'classnames'
import { Link } from 'react-router'

import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { Tag } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from '../Cells.module.scss'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel
  offerLink: string
  rowId: string
  displayThumb?: boolean
  className?: string
  isNewCollectiveOffersStructureActive: boolean
}

export const OfferNameCell = ({
  offer,
  offerLink,
  rowId,
  displayThumb = false,
  className,
  isNewCollectiveOffersStructureActive,
}: OfferNameCellProps) => {
  return (
    <th
      scope="row"
      className={classNames(
        styles['offers-table-cell'],
        styles['title-column'],
        className
      )}
      id={rowId}
    >
      <Link
        className={classNames({
          [styles['title-column-with-thumb']]: displayThumb,
        })}
        to={offerLink}
      >
        {displayThumb && (
          <div className={styles['title-column-thumb']}>
            <Thumb url={offer.imageUrl} />
          </div>
        )}
        <div>
          {offer.isShowcase && <Tag label="Offre vitrine" />}
          <div className={styles['title-column-name']}>
            {!offer.isShowcase && isNewCollectiveOffersStructureActive ? (
              <span>{`N°${offer.id}`}</span>
            ) : null}
            <span>{offer.name}</span>
          </div>
        </div>
      </Link>
    </th>
  )
}
