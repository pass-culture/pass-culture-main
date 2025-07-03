import { Link } from 'react-router'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { Tag } from 'design-system/Tag/Tag'
import styles from 'styles/components/Cells.module.scss'

interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel
  offerLink: string
  displayLabel?: boolean
}

export const OfferNameCell = ({
  offer,
  offerLink,
  displayLabel = false,
}: OfferNameCellProps) => {
  return (
    <Link className={styles['title-column-with-thumb']} to={offerLink}>
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
  )
}
