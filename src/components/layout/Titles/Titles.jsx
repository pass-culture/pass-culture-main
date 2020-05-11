import PropTypes from 'prop-types'
import React from 'react'

const Titles = ({ action, subtitle, title }) => (
  <div className="section hero-section">
    <div className="title-subtitle-link-block">
      {subtitle && <h2>
        {subtitle.toUpperCase()}
                   </h2>}
      {action && <div className="title-action-links">
        {action}
                 </div>}
    </div>
    <h1>
      {title}
    </h1>
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
