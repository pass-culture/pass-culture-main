import type { GetVenueResponseModel } from '@/apiClient/v1'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { SummarySubSubSection } from '@/components/SummaryLayout/SummarySubSubSection'

import styles from './OpeningHoursAndAddressReadOnly.module.scss'
import { OpeningHoursReadOnly } from './OpeningHoursReadOnly'

type OpeningHoursAndAddressReadOnlyProps = {
  openingHours: GetVenueResponseModel['openingHours']
  address?: GetVenueResponseModel['location']
}

export function OpeningHoursAndAddressReadOnly({
  openingHours,
  address,
}: OpeningHoursAndAddressReadOnlyProps) {
  return (
    <SummarySubSubSection title="Adresse et horaires">
      <span className={styles['opening-hours-address']}>
        {`Adresse : ${getFormattedAddress(address)}`}
      </span>

      <OpeningHoursReadOnly openingHours={openingHours} />
    </SummarySubSubSection>
  )
}
