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
        <th id="collective-offer-head-checkbox">
          <span className="visually-hidden">Case à cocher</span>
        </th>
        {isCollectiveOffersExpirationEnabled && (
          <th
            id="collective-offer-head-expiration"
            className={styles['expiration-date-th']}
          >
            <span className="visually-hidden">
              Information sur l’expiration
            </span>
          </th>
        )}
        <th id="collective-offer-head-image">
          <span className="visually-hidden">Image</span>
        </th>
        <th id="collective-offer-head-name">
          <span className="visually-hidden">Nom</span>
        </th>

        {isCollectiveOffersExpirationEnabled && (
          <th id="collective-offer-head-event-date">Date de l’évènement</th>
        )}
        <th id="collective-offer-head-venue">Lieu</th>
        <th id="collective-offer-head-institution">Établissement</th>
        <th id="collective-offer-head-status">Statut</th>
        <th
          className={classNames('th-actions', 'th-actions-eac')}
          id="collective-offer-head-actions"
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
