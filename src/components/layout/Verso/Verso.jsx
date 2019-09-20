import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import isEqual from 'lodash.isequal'

import VersoContentOfferContainer from './VersoContent/VersoContentOffer/VersoContentOfferContainer'
import VersoContentTutoContainer from './VersoContent/VersoContentTuto/VersoContentTutoContainer'
import VersoControlsContainer from './VersoControls/VersoControlsContainer'
import VersoHeaderContainer from './VersoHeader/VersoHeaderContainer'
import AbsoluteFooterContainer from '../AbsoluteFooter/AbsoluteFooterContainer'

class Verso extends React.PureComponent {
  constructor(props) {
    super(props)
    this.versoWrapper = React.createRef()
  }

  componentDidUpdate(prevProps) {
    const propsHaveBeenUpdated = !isEqual(prevProps, this.props)

    if (propsHaveBeenUpdated) {
      this.versoWrapper.current.scrollTo(0, 0)
    }
  }

  render() {
    const {
      areDetailsVisible,
      backgroundColor,
      contentInlineStyle,
      extraClassName,
      isTuto,
      offerName,
      offerType,
      offerVenueNameOrPublicName,
    } = this.props

    return (
      <div
        className={classnames('verso is-overlay', extraClassName, {
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
            type={offerType}
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
  offerType: null,
  offerVenueNameOrPublicName: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  backgroundColor: PropTypes.string,
  contentInlineStyle: PropTypes.shape(),
  extraClassName: PropTypes.string,
  isTuto: PropTypes.bool,
  offerName: PropTypes.string,
  offerType: PropTypes.string,
  offerVenueNameOrPublicName: PropTypes.string,
}

export default Verso
