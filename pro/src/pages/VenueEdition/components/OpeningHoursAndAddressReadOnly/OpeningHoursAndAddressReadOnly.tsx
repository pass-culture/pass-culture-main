import type { LocationResponseModelV2 } from '@/apiClient/v1'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursAndAddressReadOnly.module.scss'
import { OpeningHoursReadOnly } from './OpeningHoursReadOnly'

type OpeningHoursAndAddressReadOnlyProps = {
  openingHours: GetVenueResponseModel['openingHours']
  address: LocationResponseModelV2
}

export function OpeningHoursAndAddressReadOnly({
  openingHours,
  address,
}: OpeningHoursAndAddressReadOnlyProps) {
  return (
    <SummarySubSection title="Adresse et horaires" shouldShowDivider={false}>
      <span className={styles['opening-hours-address']}>
        {`Adresse : ${getFormattedAddress(address)}`}
      </span>

      <OpeningHoursReadOnly openingHours={openingHours} />
    </SummarySubSection>
  )
}
