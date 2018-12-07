import React from 'react'
import { formatSiren } from '../../../utils/input'

const PendingOffererItem = ({ offerer }) => (
  <li className="offerer-item pending">
    <div className="list-content">
      <p>
        <span className="name">{offerer.name}</span> (SIREN:{' '}
        {formatSiren(offerer.siren)})
      </p>
      <p className="is-italic mb12" id="offerer-item-validation">
        Rattachement en cours de validation par la structure
      </p>
    </div>
  </li>
)

export default PendingOffererItem
