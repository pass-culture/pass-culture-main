import classNames from 'classnames'

import { Audience } from 'core/shared/types'
import { useActiveFeature } from 'hooks/useActiveFeature'

type OffersTableHeadProps = {
  audience: Audience
}

export const OffersTableHead = ({
  audience,
}: OffersTableHeadProps): JSX.Element => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <thead>
      <tr>
        <th colSpan={3} />

        <th>
          {offerAddressEnabled && audience === Audience.INDIVIDUAL
            ? 'Adresse'
            : 'Lieu'}
        </th>
        <th>{audience === Audience.COLLECTIVE ? 'Établissement' : 'Stocks'}</th>
        <th>Statut</th>
        <th
          className={classNames('th-actions', {
            ['th-actions-eac']: audience === Audience.COLLECTIVE,
          })}
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
