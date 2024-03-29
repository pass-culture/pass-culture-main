import React from 'react'

interface TitlesProps {
  action?: JSX.Element
  description?: string
  subtitle?: string
  title: string
}

const Titles = ({
  action,
  description,
  subtitle,
  title = 'Valeur par défault',
}: TitlesProps) => {
  return (
    <div className="section hero-section">
      <div className="title-subtitle-link-block">
        <h1>{title}</h1>
        {action && <div className="title-action-links">{action}</div>}
      </div>
      {subtitle && <h2 className="subtitle">{subtitle.toUpperCase()}</h2>}
      {description && <div className="title-description">{description}</div>}
    </div>
  )
}

export default Titles
