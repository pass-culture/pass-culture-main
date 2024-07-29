import classNames from 'classnames'

import { useActiveFeature } from 'hooks/useActiveFeature'

import styles from './IndividualOffersTableHead.module.scss'

export const IndividualOffersTableHead = (): JSX.Element => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <thead className={styles['individual-offers-thead']}>
      <tr>
        <th colSpan={3} />

        <th className={styles['individual-th']}>
          {offerAddressEnabled ? 'Adresse' : 'Lieu'}
        </th>
        <th className={styles['individual-th']}>Stocks</th>
        <th className={styles['individual-th']}>Statut</th>
        <th
          className={classNames(
            styles['individual-th'],
            styles['individualth-actions']
          )}
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
