import classNames from 'classnames'
import { isAfter } from 'date-fns'

import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { getDepartmentCode } from 'commons/utils/getDepartmentCode'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import waitFullIcon from 'icons/full-wait.svg'
import styles from 'styles/components/Cells.module.scss'

export type OfferBookingCellProps = {
  rowId: string
  offer: ListOffersOfferResponseModel
  className?: string
}

export const OfferBookingCell = ({
  rowId,
  offer,
  className,
}: OfferBookingCellProps) => {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const departmentCode = getDepartmentCode(offer)

  const bookableDate =
    [OfferStatus.SCHEDULED, OfferStatus.PUBLISHED].includes(offer.status) &&
    offer.bookingAllowedDatetime &&
    isAfter(offer.bookingAllowedDatetime, new Date())
      ? formatLocalTimeDateString(
          offer.bookingAllowedDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : null

  return (
    <td
      role="cell"
      className={classNames(
        className,
        styles['offers-table-cell'],
        styles['bookings-column']
      )}
      headers={`${rowId} ${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_BOOKINGS.id}`}
    >
      <span
        className={styles['offers-table-cell-mobile-label']}
        aria-hidden={true}
      >
        {`${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_BOOKINGS.title} :`}
      </span>
      {bookableDate ? (
        <span style={{ whiteSpace: 'nowrap' }}>
          <Tag
            label={bookableDate}
            icon={waitFullIcon}
            variant={TagVariant.WARNING}
          />
        </span>
      ) : (
        offer.bookingsCount || '-'
      )}
    </td>
  )
}
