/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import { noop } from '../../../utils/functionnals'

const ActivationButton = ({ children, className, onClickHandler, style }) => (
  <Link
    style={{ ...style }}
    to="/activation/events"
    onClick={onClickHandler}
    className={`activation-button ${className}`}
  >
    {children || <span className="is-block">Activer</span>}
  </Link>
)

ActivationButton.defaultProps = {
  children: null,
  className: '',
  onClickHandler: noop,
  style: {},
}

ActivationButton.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  onClickHandler: PropTypes.func,
  style: PropTypes.object,
}

export default ActivationButton
