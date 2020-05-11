import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../layout/Icon'

function IsDuoCell({ isDuo }) {
  return (
    <span className="bookings-duo">
      {isDuo && <Icon
        alt="Réservation DUO"
        svg="ico-duo"
                />}
    </span>
  )
}

IsDuoCell.propTypes = {
  isDuo: PropTypes.bool.isRequired,
}

export default IsDuoCell
