import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { CELLS_DEFINITIONS } from 'components/OffersTable/utils/cellDefinitions'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import fullBoostedIcon from 'icons/full-boosted.svg'
import styles from 'styles/components/Cells.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

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
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps({})

  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['status-column'],
        className
      )}
      headers={`${rowId} ${CELLS_DEFINITIONS.STATUS.id}`}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {`${CELLS_DEFINITIONS.STATUS.title} :`}
        </span>
      )}
      <div className={styles['status-column-content']}>
        <StatusLabel status={status} />
        {isHeadline && (
          <Tooltip
            content={'Offre à la une'}
            visuallyHidden={isTooltipHidden}
            tooltipContentClassName={styles['headline-offer-tooltip']}
          >
            <span {...tooltipProps}>
              <SvgIcon
                src={fullBoostedIcon}
                alt="Offre à la une"
                width="20"
                className={styles['status-column-boosted-icon']}
              />
            </span>
          </Tooltip>
        )}
      </div>
    </td>
  )
}
