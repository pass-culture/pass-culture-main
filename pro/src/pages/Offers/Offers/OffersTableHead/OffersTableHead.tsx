import classNames from 'classnames'

import { Audience } from 'core/shared/types'

type OffersTableHeadProps = {
  audience: Audience
}

export const OffersTableHead = ({
  audience,
}: OffersTableHeadProps): JSX.Element => {
  return (
    <thead>
      <tr>
        <th colSpan={3} />

        <th>Lieu</th>
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
