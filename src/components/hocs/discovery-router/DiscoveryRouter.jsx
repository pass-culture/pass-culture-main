import PropTypes from 'prop-types'
import React from 'react'

import DiscoveryContainer from '../../pages/discovery/DiscoveryContainer'
import DiscoveryContainerV2 from '../../pages/discovery-v2/DiscoveryContainer'

const DiscoveryRouter = ({ isDiscoveryV2Active }) =>
  isDiscoveryV2Active ? <DiscoveryContainerV2 /> : <DiscoveryContainer />

DiscoveryRouter.defaultProps = {
  isDiscoveryV2Active: false,
}

DiscoveryRouter.propTypes = {
  isDiscoveryV2Active: PropTypes.bool,
}

export default DiscoveryRouter
