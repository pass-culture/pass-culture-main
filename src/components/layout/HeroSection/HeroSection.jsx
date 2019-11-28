import PropTypes from 'prop-types'
import React from 'react'

const HeroSection = ({ children, subtitle, title }) => (
  <div className="section hero-section">
    <div className="section-icon-mask">
      <div className="section-icon" />
    </div>

    {subtitle &&
      <h2>
        {subtitle.toUpperCase()}
      </h2>}
    <h1>
      {title}
    </h1>
    {children}
  </div>
)

HeroSection.defaultProps = {
  children: null,
  subtitle: null,
}

HeroSection.propTypes = {
  children: PropTypes.node,
  subtitle: PropTypes.string,
  title: PropTypes.string.isRequired,
}

export default HeroSection
