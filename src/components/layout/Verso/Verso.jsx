import PropTypes from 'prop-types'
import React, { createRef, PureComponent } from 'react'

import VersoContentOfferContainer from './VersoContent/VersoContentOffer/VersoContentOfferContainer'
import VersoControlsContainer from './VersoControls/VersoControlsContainer'
import VersoHeaderContainer from './VersoHeader/VersoHeaderContainer'

class Verso extends PureComponent {
  constructor(props) {
    super(props)
    this.versoWrapper = createRef()
  }

  componentDidUpdate(prevProps) {
    const propsHaveBeenUpdated = prevProps !== this.props

    if (propsHaveBeenUpdated) {
      this.versoWrapper.current.scrollTop = 0
    }
  }

  render() {
    const {
      areDetailsVisible,
      extraClassName,
      offerName,
      offerType,
      offerVenueNameOrPublicName,
    } = this.props

    return (
      <div className={`verso is-overlay ${extraClassName} ${areDetailsVisible ? 'flipped' : ''}`}>
        <div
          className="verso-wrapper"
          ref={this.versoWrapper}
        >
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
  }
}

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
