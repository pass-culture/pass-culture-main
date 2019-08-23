import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import VersoContentOfferContainer from './verso-content/VersoContentOffer/VersoContentOfferContainer'
import VersoContentTutoContainer from './verso-content/VersoContentTuto/VersoContentTutoContainer'
import VersoControlsContainer from './VersoControls/VersoControlsContainer'
import VersoHeaderContainer from './verso-content/VersoHeaderContainer'
import AbsoluteFooterContainer from '../AbsoluteFooter/AbsoluteFooterContainer'

class Verso extends React.PureComponent {
  constructor(props) {
    super(props)
    this.versoWrapper = React.createRef()
  }

  componentDidUpdate() {
    this.versoWrapper.current.scrollTo(0, 0)
  }

  render() {
    const {
      areDetailsVisible,
      backgroundColor,
      contentInlineStyle,
      extraClassName,
      isTuto,
      offerName,
      offerVenueNameOrPublicName,
    } = this.props

    return (
      <div
        className={classnames('verso', extraClassName, {
          flipped: areDetailsVisible,
        })}
      >
        <div
          className="verso-wrapper"
          ref={this.versoWrapper}
        >
          <VersoHeaderContainer
            backgroundColor={backgroundColor}
            subtitle={offerVenueNameOrPublicName}
            title={offerName}
          />
          {!isTuto && <VersoControlsContainer />}
          <div
            className="verso-content"
            style={contentInlineStyle}
          >
            {isTuto ? <VersoContentTutoContainer /> : <VersoContentOfferContainer />}
          </div>
        </div>
        <AbsoluteFooterContainer
          areDetailsVisible={areDetailsVisible}
          borderTop
          colored={!isTuto}
          id="verso-footer"
        />
      </div>
    )
  }
}

Verso.defaultProps = {
  backgroundColor: null,
  contentInlineStyle: null,
  extraClassName: null,
  isTuto: null,
  offerName: null,
  offerVenueNameOrPublicName: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  backgroundColor: PropTypes.string,
  contentInlineStyle: PropTypes.shape(),
  extraClassName: PropTypes.string,
  isTuto: PropTypes.bool,
  offerName: PropTypes.string,
  offerVenueNameOrPublicName: PropTypes.string,
}

export default Verso
