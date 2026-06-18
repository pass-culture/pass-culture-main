import type {
  GetVenueResponseModel,
  LocationResponseModelV2,
} from '@/apiClient/v1'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from './AddressAndOpeningHourSubSection.module.scss'
import { OpeningHours } from './OpeningHours'

interface OpeningHoursAndAddressSubSectionProps {
  address: LocationResponseModelV2
  openingHours: GetVenueResponseModel['openingHours']
}
export function AddressAndOpeningHourSubSection({
  address,
  openingHours,
}: Readonly<OpeningHoursAndAddressSubSectionProps>) {
  return (
    <SummarySubSection title="Adresse et horaires" shouldShowDivider={false}>
      <span className={styles['opening-hours-address']}>
        {`Adresse : ${getFormattedAddress(address)}`}
      </span>

      <OpeningHours openingHours={openingHours} />
    </SummarySubSection>
  )
}
