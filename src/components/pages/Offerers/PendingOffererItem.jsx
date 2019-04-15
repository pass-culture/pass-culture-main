import React from 'react'
import { formatSire } from 'utils/sire'

const PendingOffererItem = ({ offerer }) => (
  <li className="offerer-item pending">
    <div className="list-content">
      <p>
        <span className="name">{offerer.name}</span> (SIREN:{' '}
        {formatSire(offerer.siren)})
      </p>
      <p className="is-italic mb12" id="offerer-item-validation">
        Rattachement en cours de validation par la structure
      </p>
    </div>
  </li>
)

export default PendingOffererItem
