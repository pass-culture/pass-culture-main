import { isAfter } from 'date-fns'

import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { StatusLabel } from '@/components/StatusLabel/StatusLabel'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullWaitIcon from '@/icons/full-wait.svg'

import styles from './OfferPublicationEditionTags.module.scss'

export type OfferPublicationEditionProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function OfferPublicationEditionTags({
  offer,
}: Readonly<OfferPublicationEditionProps>) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  if (offer.status === OfferStatus.INACTIVE) {
    return <StatusLabel status={offer.status} />
  }

  const departmentCode = getDepartmentCode(offer, selectedPartnerVenue)

  const publicationDate =
    offer.publicationDatetime && isAfter(offer.publicationDatetime, new Date())
      ? formatLocalTimeDateString(
          offer.publicationDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : null

  const bookingAllowedDate =
    offer.bookingAllowedDatetime &&
    isAfter(offer.bookingAllowedDatetime, new Date())
      ? formatLocalTimeDateString(
          offer.bookingAllowedDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : null

  return (
    <div className={styles['container']}>
      {[OfferStatus.ACTIVE, OfferStatus.PUBLISHED].includes(offer.status) && (
        <StatusLabel status={offer.status} />
      )}
      {offer.status === OfferStatus.SCHEDULED && publicationDate && (
        <Tag
          variant={TagVariant.WARNING}
          icon={fullWaitIcon}
          label={`Publication : ${publicationDate}`}
        />
      )}
      {[OfferStatus.PUBLISHED, OfferStatus.SCHEDULED].includes(offer.status) &&
        bookingAllowedDate && (
          <Tag
            variant={TagVariant.WARNING}
            icon={fullWaitIcon}
            label={`Réservabilité : ${bookingAllowedDate}`}
          />
        )}
    </div>
  )
}
