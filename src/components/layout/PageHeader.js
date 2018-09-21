/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import HistoryBackButton from './HistoryBackButton'
import HistoryCloseButton from './HistoryCloseButton'

const PageHeader = ({ useBack, useClose, className, theme, title }) => (
  <header className={`pc-theme-${theme} pc-header is-relative ${className}`}>
    <h1>
      <span>{title}</span>
      {useBack && !useClose && <HistoryBackButton theme={theme} />}
      {useClose && <HistoryCloseButton theme={theme} />}
    </h1>
  </header>
)

PageHeader.defaultProps = {
  className: '',
  theme: 'red',
  useBack: true,
  useClose: false,
}

PageHeader.propTypes = {
  className: PropTypes.string,
  theme: PropTypes.string,
  title: PropTypes.string.isRequired,
  useBack: PropTypes.bool,
  useClose: PropTypes.bool,
}

export default PageHeader
