import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

export const RawPageCloseButton = ({
  baseurl,
  className,
  disabled,
  history,
  theme,
}) => (
  <span
    style={{ right: 0 }}
    className={`pc-theme-${theme} is-absolute mr12 ${className}`}
  >
    {/* FIXME: Quand les choses seront stables apres octobre on gérera le close/back button du header via un css ou une prop `type` */}
    <button
      type="button"
      disabled={disabled}
      id="close-back-button"
      onClick={() => history.push(`/${baseurl}`)}
      className="no-border no-background no-outline"
    >
      <span aria-hidden className="icon-legacy-close" title="" />
    </button>
  </span>
)

RawPageCloseButton.defaultProps = {
  baseurl: 'decouverte',
  className: '',
  disabled: false,
  theme: 'red',
}

RawPageCloseButton.propTypes = {
  baseurl: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  history: PropTypes.object.isRequired,
  theme: PropTypes.string,
}

export default withRouter(RawPageCloseButton)
