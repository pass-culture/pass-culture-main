import classNames from 'classnames'
import { Link } from 'react-router'
import styles from 'styles/components/Cells.module.scss'

import { CollectiveOfferResponseModel } from '@/apiClient//v1'
import { getCellsDefinition } from '@/components/OffersTable/utils/cellDefinitions'
import { Tag } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel
  offerLink: string
  rowId: string
  displayLabel?: boolean
  displayThumb?: boolean
  className?: string
}

export const OfferNameCell = ({
  offer,
  offerLink,
  rowId,
  displayLabel = false,
  displayThumb = false,
  className,
}: OfferNameCellProps) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['title-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().NAME.id}`}
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
            {displayLabel && (
              <span
                className={styles['offers-table-cell-mobile-label']}
                aria-hidden={true}
              >
                {`${getCellsDefinition().NAME.title} :`}
              </span>
            )}
            {offer.name}
          </div>
        </div>
      </Link>
    </td>
  )
}
