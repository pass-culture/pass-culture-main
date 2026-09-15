import { isAfter } from 'date-fns'

import { type ListOffersOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { StatusLabel } from '@/components/StatusLabel/StatusLabel'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import waitFullIcon from '@/icons/full-wait.svg'

import styles from './OfferStatusCell.module.scss'

export type OfferStatusCellProps = {
  offer: ListOffersOfferResponseModel
}

export const OfferStatusCell = ({ offer }: OfferStatusCellProps) => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const departmentCode = getDepartmentCode(offer, selectedPartnerVenue)

  const publicationDate =
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
    </div>
  )
}
