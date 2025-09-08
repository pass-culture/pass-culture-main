import classNames from 'classnames'

import type { GetCollectiveOfferLocationModel } from '@/apiClient/adage'
import { CollectiveLocationType } from '@/apiClient/v1'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'

import styles from '../Cells.module.scss'

export interface OfferLocationCellProps {
  rowId: string
  offerLocation?: GetCollectiveOfferLocationModel | null
}

export const OfferLocationCell = ({
  rowId,
  offerLocation,
}: OfferLocationCellProps) => {
  const getLocation = () => {
    if (offerLocation?.locationType === CollectiveLocationType.TO_BE_DEFINED) {
      return 'À déterminer'
    }

    if (offerLocation?.locationType === CollectiveLocationType.SCHOOL) {
      return "Dans l'établissement"
    }

    const { label, street, postalCode, city } = offerLocation?.address || {}
    return (
      <div className={styles['text-overflow-ellipsis']}>
        {label ? `${label} - ` : ''}
        {street} {postalCode} {city}
      </div>
    )
  }

  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['location-column']
      )}
      headers={`${rowId} ${getCellsDefinition().LOCATION.id}`}
    >
      {getLocation()}
    </td>
  )
}
