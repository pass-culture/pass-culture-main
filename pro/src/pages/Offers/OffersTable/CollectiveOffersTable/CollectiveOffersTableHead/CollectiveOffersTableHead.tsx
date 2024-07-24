import classNames from 'classnames'

import { useActiveFeature } from 'hooks/useActiveFeature'

import styles from './CollectiveOffersTableHead.module.scss'

export const CollectiveOffersTableHead = (): JSX.Element => {
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )
  return (
    <thead>
      <tr>
        <th className={styles['offer-reference-th']} />
        <th>
          <span className={styles['visually-hidden']}>Case à cocher</span>
        </th>
        {isCollectiveOffersExpirationEnabled && (
          <th className={styles['expiration-date-th']}>
            <span className={styles['visually-hidden']}>
              Information sur l’expiration
            </span>
          </th>
        )}
        <th>
          <span className={styles['visually-hidden']}>Image</span>
        </th>
        <th>
          <span className={styles['visually-hidden']}>Nom</span>
        </th>

        {isCollectiveOffersExpirationEnabled && <th>Date de l’évènement</th>}
        <th>Lieu</th>
        <th>Établissement</th>
        <th>Statut</th>
        <th className={classNames('th-actions', 'th-actions-eac')}>Actions</th>
      </tr>
    </thead>
  )
}
