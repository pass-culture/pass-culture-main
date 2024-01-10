import cn from 'classnames'
import { NavLink } from 'react-router-dom'

import styles from './DomainsCard.module.scss'

export interface DomainsCardProps {
  title: string
  color: string
  src: string
  href: string
  handlePlaylistElementTracking: () => void
}

const DomainsCard = ({
  title,
  color,
  src,
  href,
  handlePlaylistElementTracking,
}: DomainsCardProps) => {
  return (
    <NavLink
      className={cn(styles['container'], styles[`container-${color}`])}
      to={href}
      onClick={() => handlePlaylistElementTracking()}
    >
      <img src={src} alt="" className={styles['container-img']} />
      <div className={styles['container-title']}>{title}</div>
    </NavLink>
  )
}

export default DomainsCard
