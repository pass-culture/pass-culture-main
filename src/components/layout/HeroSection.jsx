import React from 'react'

const HeroSection = ({ children, subtitle, title }) => {
  return (
    <div className="section hero-section">
      {subtitle && (
        <h2 className="has-text-weight-bold is-paddingless">{subtitle}</h2>
      )}

      <h1>{title}</h1>

      {children}
    </div>
  )
}

export default HeroSection
