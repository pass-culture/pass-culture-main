import PropTypes from 'prop-types'
import React, { useState, useEffect } from 'react'

import VersoContentOfferContainer from './VersoContent/VersoContentOffer/VersoContentOfferContainer'
import VersoControlsContainer from './VersoControls/VersoControlsContainer'
import VersoHeaderContainer from './VersoHeader/VersoHeaderContainer'
import LoaderContainer from '../Loader/LoaderContainer'

const Verso = ({
  areDetailsVisible,
  extraClassName,
  offerName,
  subcategory,
  offerVenueNameOrPublicName,
}) => {
  const [isLoading, setIsLoading] = useState(offerName === null)

  useEffect(() => {
    offerName && setIsLoading(false)
  }, [offerName])

  return isLoading ? (
    <LoaderContainer />
  ) : (
    <div className={`verso is-overlay ${extraClassName} ${areDetailsVisible ? 'flipped' : ''}`}>
      <div className="verso-wrapper">
        <VersoHeaderContainer
          subcategory={subcategory}
          subtitle={offerVenueNameOrPublicName}
          title={offerName}
        />
        <VersoControlsContainer />
        <div className="mosaic-background verso-content">
          <VersoContentOfferContainer />
        </div>
      </div>
    </div>
  )
}

Verso.defaultProps = {
  extraClassName: '',
  offerName: null,
  offerVenueNameOrPublicName: null,
  subcategory: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  offerName: PropTypes.string,
  offerVenueNameOrPublicName: PropTypes.string,
  subcategory: PropTypes.string,
}

export default Verso
