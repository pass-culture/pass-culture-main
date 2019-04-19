import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import VersoHeader from './verso-content/VersoHeader'
import VersoControl from './verso-controls/VersoControlContainer'
import VersoContentOfferContainer from './verso-content/verso-content-offer/VersoContentOfferContainer'
import VersoContentTuto from './verso-content/VersoContentTuto'
import Footer from '../layout/Footer'

class Verso extends React.PureComponent {
  render() {
    const {
      areDetailsVisible,
      backgroundColor,
      contentInlineStyle,
      extraClassName,
      forceDetailsVisible,
      isTuto,
      imageURL,
      offerName,
      offerVenueNameOrPublicName,
    } = this.props

    const flipped = forceDetailsVisible || areDetailsVisible
    return (
      <div
        className={classnames('verso is-overlay', extraClassName, {
          flipped,
        })}
      >
        <div className="verso-wrapper is-black-text scroll-y flex-rows is-relative text-left">
          <VersoHeader
            title={offerName}
            subtitle={offerVenueNameOrPublicName}
            backgroundColor={backgroundColor}
          />
          {!isTuto && <VersoControl />}
          <div className="verso-content" style={contentInlineStyle}>
            {!isTuto && <VersoContentOfferContainer />}
            {isTuto && <VersoContentTuto imageURL={imageURL} />}
          </div>
        </div>
        <Footer id="verso-footer" borderTop colored={!isTuto} />
      </div>
    )
  }
}

Verso.defaultProps = {
  backgroundColor: null,
  extraClassName: null,
  forceDetailsVisible: false,
  imageURL: '',
  offerName: null,
  offerVenueNameOrPublicName: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  backgroundColor: PropTypes.string,
  contentInlineStyle: PropTypes.object.isRequired,
  extraClassName: PropTypes.string,
  forceDetailsVisible: PropTypes.bool,
  imageURL: PropTypes.string,
  isTuto: PropTypes.bool.isRequired,
  offerName: PropTypes.string,
  offerVenueNameOrPublicName: PropTypes.string,
}

export default Verso
