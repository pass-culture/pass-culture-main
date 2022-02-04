import PropTypes from 'prop-types'
import React from 'react'

import { formatSirenOrSiret } from 'utils/siren'

const PendingOffererItem = ({ offerer }) => (
  <li className="offerer-item pending">
    <div className="list-content">
      <p>
        <span className="name">{offerer.name}</span>
        {` (SIREN: ${formatSirenOrSiret(offerer.siren)})`}
      </p>
      <p className="validating-status" id="offerer-item-validation">
        Rattachement en cours de validation
      </p>
    </div>
  </li>
)

PendingOffererItem.propTypes = {
  offerer: PropTypes.shape().isRequired,
}

export default PendingOffererItem
