import { isAfter } from 'date-fns'

import { ListOffersOfferResponseModel, OfferStatus } from '@/apiClient//v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { StatusLabel } from '@/components/StatusLabel/StatusLabel'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullBoostedIcon from '@/icons/full-boosted.svg'
import waitFullIcon from '@/icons/full-wait.svg'
import styles from '@/pages/IndividualOffers/IndividualOffersContainer/components/IndividualOfferColumns/components/Cells.module.scss'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

export type OfferStatusCellProps = {
  offer: ListOffersOfferResponseModel
  isHeadline?: boolean
}

export const OfferStatusCell = ({
  offer,
  isHeadline,
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
  )
}
