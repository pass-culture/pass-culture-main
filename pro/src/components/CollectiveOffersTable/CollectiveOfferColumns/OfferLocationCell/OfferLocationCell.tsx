import type { GetCollectiveOfferLocationModel } from '@/apiClient/v1'
import { CollectiveLocationType } from '@/apiClient/v1'

import styles from './OfferLocationCell.module.scss'

export interface OfferLocationCellProps {
  offerLocation?: GetCollectiveOfferLocationModel | null
}

export const OfferLocationCell = ({
  offerLocation,
}: OfferLocationCellProps) => {
  const getLocation = () => {
    if (offerLocation?.locationType === CollectiveLocationType.TO_BE_DEFINED) {
      return 'À déterminer'
    }

    if (offerLocation?.locationType === CollectiveLocationType.SCHOOL) {
      return "Dans l'établissement"
    }

    const { label, street, postalCode, city } = offerLocation?.location || {}
    return (
      <>
        {label ? `${label} - ` : ''}
        {street} {postalCode} {city}
      </>
    )
  }

  return <p className={styles['location-cell']}>{getLocation()}</p>
}
