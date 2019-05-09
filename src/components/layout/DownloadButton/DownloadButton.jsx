import PropTypes from 'prop-types'
import React from 'react'

const DownloadButton = ({ children, downloadFileOrNotifyAnError }) => (
  <button
    className="button is-primary"
    onClick={downloadFileOrNotifyAnError}
    type="button">
    {children}
  </button>
)

DownloadButton.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
}

export default DownloadButton
