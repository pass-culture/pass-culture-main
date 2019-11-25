import PropTypes from 'prop-types'
import React from 'react'

import AbsoluteFooterContainer from '../../../../../layout/AbsoluteFooter/AbsoluteFooterContainer'

const QrCode = ({ humanizedBeginningDatetime, offerName, qrCode, token, venueName }) => (
  <div className="qr-code">
    <div className="qr-code-white-card">
      <div className="qr-code-header">
        <div className="qr-code-offer-name">
          {offerName}
        </div>
        <p className="qr-code-offer-beginning-datetime">
          {humanizedBeginningDatetime}
        </p>
        <p className="qr-code-venue-name">
          {venueName}
        </p>
      </div>

      <div className="qr-code-token">
        {token.toLowerCase()}
      </div>
      <div className="qr-code-image">
        <img
          alt=""
          src={qrCode}
        />
      </div>
    </div>
    <AbsoluteFooterContainer
      areDetailsVisible={false}
      borderTop
      colored
      id="verso-footer"
    />
  </div>
)

QrCode.defaultProps = {
  qrCode: null,
}

QrCode.propTypes = {
  humanizedBeginningDatetime: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
  qrCode: PropTypes.string,
  token: PropTypes.string.isRequired,
  venueName: PropTypes.string.isRequired,
}

export default QrCode
