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
    <div className={`section ${styles['hero-section']}`}>
      <div className={styles['title-subtitle-link-block']}>
        <h1 className={styles['title']}>{title}</h1>
        {action && <div className={styles['title-action-links']}>{action}</div>}
      </div>
      {subtitle && (
        <h2 className={styles['subtitle']}>{subtitle.toUpperCase()}</h2>
      )}
      {description && (
        <div className={styles['title-description']}>{description}</div>
      )}
    </div>
  )
}
