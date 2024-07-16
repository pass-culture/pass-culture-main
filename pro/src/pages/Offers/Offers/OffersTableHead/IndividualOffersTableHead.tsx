import classNames from 'classnames'

import { useActiveFeature } from 'hooks/useActiveFeature'

export const IndividualOffersTableHead = (): JSX.Element => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <thead>
      <tr>
        <th colSpan={3} />

        <th>{offerAddressEnabled ? 'Adresse' : 'Lieu'}</th>
        <th>Stocks</th>
        <th>Statut</th>
        <th className={classNames('th-actions')}>Actions</th>
      </tr>
    </thead>
  )
}
