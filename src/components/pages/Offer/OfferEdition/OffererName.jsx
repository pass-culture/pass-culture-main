import React from 'react'
import PropTypes from 'prop-types'

export const OffererName = ({ name }) => (
  <div className="field field-select is-horizontal readonly">
    <div className="field-label readonly">
      {'Structure :'}
    </div>
    <div className="field-body field-content">
      {name}
    </div>
  </div>
)

OffererName.propTypes = {
  name: PropTypes.string.isRequired,
}
