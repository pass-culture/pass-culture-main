/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const PageSubmitButton = ({ className, disabled, isloading, theme }) => (
  <span
    style={{ right: 0 }}
    className={`pc-theme-${theme} is-absolute mr12 ${className}`}
  >
    {/* FIXME: Quand les choses seront stables apres octobre on gérera le close/back/submit button du header via un css ou une prop `type` */}
    {!isloading && (
      <button
        type="submit"
        disabled={disabled}
        id="page-submit-button"
        className="fs13 border-all no-background no-outline px7 py3"
      >
        <span className="is-semi-bold">OK</span>
      </button>
    )}
    {isloading && (
      <span className="fs18">
        <span className="animate-spin icon-spin6" />
      </span>
    )}
  </span>
)

PageSubmitButton.defaultProps = {
  className: '',
  disabled: false,
  isloading: false,
  theme: 'red',
}

PageSubmitButton.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  isloading: PropTypes.bool,
  theme: PropTypes.string,
}

export default PageSubmitButton
