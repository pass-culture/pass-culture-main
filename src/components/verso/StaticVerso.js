import PropTypes from 'prop-types'
import React from 'react'

import { THUMBS_URL } from '../../utils/config'

const StaticVerso = ({ mediationId }) => (
  <img
    alt="verso"
    className="verso-tuto-mediation"
    src={`${THUMBS_URL}/mediations/${mediationId}_1`}
  />
)

StaticVerso.propTypes = {
  mediationId: PropTypes.string.isRequired,
}

export default StaticVerso
