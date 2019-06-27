import React from 'react'

const HeroSection = ({ children, subtitle, title }) => {
  return (
    <div className="section hero-section">
      <div className="section-icon-mask">
        <div className="section-icon"/>
      </div>


      <h1>{title}</h1>

      {subtitle && (
        <h2 className="has-text-weight-bold is-paddingless">{subtitle}</h2>
      )}

      {children}
    </div>
  )
}

export default HeroSection
