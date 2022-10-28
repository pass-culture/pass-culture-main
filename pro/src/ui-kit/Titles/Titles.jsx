import PropTypes from 'prop-types'
import React from 'react'

const Titles = ({ action, description, subtitle, title }) => (
  <div className="section hero-section">
    <div className="title-subtitle-link-block">
      <h1>{title}</h1>
      {action && <div className="title-action-links">{action}</div>}
    </div>
    {subtitle && <h2 className="subtitle">{subtitle.toUpperCase()}</h2>}
    {description && <div className="title-description">{description}</div>}
  </div>
)

Titles.defaultProps = {
  action: null,
  description: null,
  subtitle: null,
}

Titles.propTypes = {
  action: PropTypes.element,
  description: PropTypes.string,
  subtitle: PropTypes.string,
  title: PropTypes.string.isRequired,
}

export default Titles
