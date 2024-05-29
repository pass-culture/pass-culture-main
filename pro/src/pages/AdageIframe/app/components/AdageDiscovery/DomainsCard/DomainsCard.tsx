import cn from 'classnames'
import { Link } from 'react-router-dom'

import styles from './DomainsCard.module.scss'

export interface DomainsCardProps {
  title: string
  color: string
  src: string
  href: string
  handlePlaylistElementTracking: () => void
}

export const DomainsCard = ({
  title,
  color,
  src,
  href,
  handlePlaylistElementTracking,
}: DomainsCardProps) => {
  return (
    <Link
      data-testid="card-domain-link"
      className={cn(styles['container'], styles[`container-${color}`])}
      to={href}
      onClick={() => handlePlaylistElementTracking()}
    >
      <img src={src} alt="" className={styles['container-img']} />
      <div className={styles['container-title']}>{title}</div>
    </Link>
  )
}
