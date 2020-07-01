import PropTypes from 'prop-types'
import React from 'react'

import VersoContentOfferContainer from './VersoContent/VersoContentOffer/VersoContentOfferContainer'
import VersoControlsContainer from './VersoControls/VersoControlsContainer'
import VersoHeaderContainer from './VersoHeader/VersoHeaderContainer'

const Verso = ({
  areDetailsVisible,
  extraClassName,
  offerName,
  offerType,
  offerVenueNameOrPublicName,
}) => (
  <div className={`verso is-overlay ${extraClassName} ${areDetailsVisible ? 'flipped' : ''}`}>
    <div className="verso-wrapper">
      <VersoHeaderContainer
        subtitle={offerVenueNameOrPublicName}
        title={offerName}
        type={offerType}
      />
      <VersoControlsContainer />
      <div className="mosaic-background verso-content">
        <VersoContentOfferContainer />
      </div>
    </div>
  </div>
)

Verso.defaultProps = {
  extraClassName: '',
  offerName: null,
  offerType: null,
  offerVenueNameOrPublicName: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  offerName: PropTypes.string,
  offerType: PropTypes.string,
  offerVenueNameOrPublicName: PropTypes.string,
}

export default Verso
