import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

export const RawPageBackButton = ({ className, disabled, history, theme }) => (
  <span
    style={{ left: 0 }}
    className={`pc-theme-${theme} is-absolute ml12 ${className}`}
  >
    {/* FIXME: Quand les choses seront stables apres octobre on gérera le close/back button du header via un css ou une prop `type` */}
    <button
      type="button"
      disabled={disabled}
      id="history-back-button"
      onClick={history.goBack}
      className="no-border no-background no-outline"
    >
      <span aria-hidden className="icon-legacy-previous" title="" />
    </button>
  </span>
)

RawPageBackButton.defaultProps = {
  className: '',
  disabled: false,
  theme: 'red',
}

RawPageBackButton.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  history: PropTypes.object.isRequired,
  theme: PropTypes.string,
}

export default withRouter(RawPageBackButton)
