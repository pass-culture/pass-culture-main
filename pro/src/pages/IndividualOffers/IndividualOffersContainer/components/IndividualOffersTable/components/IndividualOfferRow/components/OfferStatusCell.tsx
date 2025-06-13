import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import fullBoostedIcon from 'icons/full-boosted.svg'
import styles from 'styles/components/Cells.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

interface OfferStatusCellProps {
  rowId: string
  status: OfferStatus
  displayLabel?: boolean
  isHeadline?: boolean
  className?: string
}

export const OfferStatusCell = ({
  rowId,
  status,
  displayLabel,
  isHeadline,
  className,
}: OfferStatusCellProps) => {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['status-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_STATUS.id}`}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {`${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_STATUS.title} :`}
        </span>
      )}
      <div className={styles['status-column-content']}>
        <StatusLabel status={status} />
        {isHeadline && (
          <div className={styles['status-column-headline-offer-star']}>
            <Tooltip content="Offre à la une">
              <button className={styles['status-column-headline-offer-button']}>
                <SvgIcon
                  src={fullBoostedIcon}
                  alt=""
                  width="20"
                  className={styles['status-column-headline-offer-star-icon']}
                />
              </button>
            </Tooltip>
          </div>
        )}
      </div>
    </td>
  )
}
