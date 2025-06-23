import classNames from 'classnames'
import { isAfter } from 'date-fns'

import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullBoostedIcon from 'icons/full-boosted.svg'
import waitFullIcon from 'icons/full-wait.svg'
import styles from 'styles/components/Cells.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

export type OfferStatusCellProps = {
  rowId: string
  offer: ListOffersOfferResponseModel
  displayLabel?: boolean
  isHeadline?: boolean
  className?: string
}

export const OfferStatusCell = ({
  rowId,
  offer,
  displayLabel,
  isHeadline,
  className,
}: OfferStatusCellProps) => {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const departmentCode = getDepartmentCode(offer)

  const publicationDate =
    isRefactoFutureOfferEnabled &&
    offer.status === OfferStatus.SCHEDULED &&
    offer.publicationDatetime &&
    isAfter(offer.publicationDatetime, new Date())
      ? formatLocalTimeDateString(
          offer.publicationDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : null

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
        {publicationDate ? (
          <Tag
            label={publicationDate}
            icon={waitFullIcon}
            variant={TagVariant.WARNING}
          />
        ) : (
          <StatusLabel status={offer.status} />
        )}
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
