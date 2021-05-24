import PropTypes from 'prop-types'
import React from 'react'

const VenueCreation = ({ isTemporary }) => {
  return (
    <div>
      <h1>
        {"i'm the venue creation page"}
      </h1>

      <p>
        {isTemporary ? 'Create a temporary venue' : 'Create a permanent venue'}
      </p>
    </div>
  )
}

VenueCreation.defaultProps = {
  isTemporary: false,
}

VenueCreation.propTypes = {
  isTemporary: PropTypes.bool,
}

export default VenueCreation
