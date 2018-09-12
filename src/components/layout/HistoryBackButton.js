import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

const HistoryBackButton = ({ className, history, theme }) => (
  <span
    style={{ left: 0 }}
    className={`pc-theme-${theme} is-absolute ml12 ${className}`}
  >
    <button
      type="button"
      onClick={history.goBack}
      className="no-border no-background no-outline"
    >
      <span aria-hidden className="icon-previous" title="" />
    </button>
  </span>
)

HistoryBackButton.defaultProps = {
  className: '',
  theme: 'red',
}

HistoryBackButton.propTypes = {
  className: PropTypes.string,
  history: PropTypes.object.isRequired,
  theme: PropTypes.string,
}

export default withRouter(HistoryBackButton)
