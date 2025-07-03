import classNames from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { Tag } from 'design-system/Tag/Tag'
import styles from 'styles/components/Cells.module.scss'
import { Thumb } from 'ui-kit/Thumb/Thumb'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel
  displayLabel?: boolean
  displayThumb?: boolean
}

export const OfferNameCell = ({
  offer,
  displayLabel = false,
  displayThumb = false,
}: OfferNameCellProps) => {
  return (
    <div
      className={classNames({
        [styles['title-column-with-thumb']]: displayThumb,
      })}
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
            <span className={styles['offers-table-cell-mobile-label']}>
              {`${getCellsDefinition().NAME.title} :`}
            </span>
          )}
          {offer.name}
        </div>
      </div>
    </div>
  )
}
