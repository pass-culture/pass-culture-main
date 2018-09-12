/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import HistoryBackButton from './HistoryBackButton'

const PageHeader = ({ canback, className, theme, title }) => (
  <header className={`pc-theme-${theme} pc-header is-relative ${className}`}>
    <h1>
      <span>{title}</span>
      {canback && <HistoryBackButton theme={theme} />}
    </h1>
  </header>
)

PageHeader.defaultProps = {
  canback: true,
  className: '',
  theme: 'red',
}

PageHeader.propTypes = {
  canback: PropTypes.bool,
  className: PropTypes.string,
  theme: PropTypes.string,
  title: PropTypes.string.isRequired,
}

export default PageHeader
