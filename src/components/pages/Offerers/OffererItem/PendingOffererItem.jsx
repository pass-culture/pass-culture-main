import React from 'react'

import { formatSirenOrSiret } from '../../../../utils/siren'

const PendingOffererItem = ({ offerer }) => (
  <li className="offerer-item pending">
    <div className="list-content">
      <p>
        <span className="name">
          {offerer.name}
        </span>
        {` (SIREN: ${formatSirenOrSiret(offerer.siren)})`}
      </p>
      <p
        className="is-italic mb12"
        id="offerer-item-validation"
      >
        {'Rattachement en cours de validation'}
      </p>
    </div>
  </li>
)

export default PendingOffererItem
