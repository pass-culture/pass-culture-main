import classNames from 'classnames'

import { useActiveFeature } from 'hooks/useActiveFeature'

export const CollectiveOffersTableHead = (): JSX.Element => {
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )
  return (
    <thead>
      <tr>
        <th colSpan={3} />

        {isCollectiveOffersExpirationEnabled && <th>Date de l’évènement</th>}
        <th>Lieu</th>
        <th>Établissement</th>
        <th>Statut</th>
        <th className={classNames('th-actions', 'th-actions-eac')}>Actions</th>
      </tr>
    </thead>
  )
}
