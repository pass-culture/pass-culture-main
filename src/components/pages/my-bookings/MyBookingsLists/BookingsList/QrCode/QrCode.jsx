import PropTypes from 'prop-types'
import React from 'react'
import AbsoluteFooterContainer from '../../../../../layout/AbsoluteFooter/AbsoluteFooterContainer'

const QrCode = props => {
  const { humanizedBeginningDatetime, offerName, qrCode, token, venueName } = props

  return (
    <div className="qr-code">
      <div className="qr-code-white-card">
        <div className="qr-code-header">
          <div className="qr-code-offer-name">{offerName}</div>
          <div className="qr-code-offer-beginning-datetime">{humanizedBeginningDatetime}</div>
          <div className="qr-code-venue-name">{venueName}</div>
        </div>

        <div className="qr-code-token">{token}</div>
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
}

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
