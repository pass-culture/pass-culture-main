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
        <th />
        <th scope="col" id="collective-th-checkbox">
          <span className="visually-hidden">Case à cocher</span>
        </th>
        <th
          scope="col"
          className="visually-hidden"
          id="collective-th-expiration-date"
        >
          <span>Date d expiration</span>
        </th>
        <th scope="col" id="collective-th-image">
          <span className="visually-hidden">Image</span>
        </th>
        <th scope="col" id="collective-th-name">
          <span className="visually-hidden">Nom</span>
        </th>

        <th scope="col" id="collective-th-venue">
          Lieu
        </th>
        <th scope="col" id="collective-th-institution">
          {audience === Audience.COLLECTIVE ? 'Établissement' : 'Stocks'}
        </th>
        <th scope="col" id="collective-th-status">
          Statut
        </th>
        <th
          scope="col"
          id="collective-th-actions"
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
