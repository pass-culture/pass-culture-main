import styles from './Titles.module.scss'

interface TitlesProps {
  action?: JSX.Element
  description?: string
  subtitle?: string
  title: string
}

export const Titles = ({
  action,
  description,
  subtitle,
  title = 'Valeur par défault',
}: TitlesProps) => {
  return (
    <div className="section hero-section">
      <div className="title-subtitle-link-block">
        <h1 className={styles['title']}>{title}</h1>
        {action && <div className="title-action-links">{action}</div>}
      </div>
      {subtitle && <h2 className="subtitle">{subtitle.toUpperCase()}</h2>}
      {description && <div className="title-description">{description}</div>}
    </div>
  )
}
