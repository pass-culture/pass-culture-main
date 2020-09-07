import PropTypes from 'prop-types'
import React from 'react'
import Title from './Title'
import Subtitle from './Subtitle'

const Titles = ({ action, subtitle, title }) => (
  <div className="section hero-section">
    <div className="title-subtitle-link-block">
      {subtitle && <Subtitle subtitle={subtitle.toUpperCase()} />}
      {action &&
      <div className="title-action-links">
        {action}
      </div>}
    </div>
    <Title title={title} />
  </div>
)

Titles.defaultProps = {
  action: null,
  subtitle: null,
}

Titles.propTypes = {
  action: PropTypes.element,
  subtitle: PropTypes.string,
  title: PropTypes.string.isRequired,
}

export default Titles
