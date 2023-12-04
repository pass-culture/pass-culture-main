import cn from 'classnames'

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
    <a
      className={cn(styles['container'], styles[`container-${color}`])}
      href={href}
      onClick={() => handlePlaylistElementTracking()}
    >
      <img src={src} alt="" className={styles['container-img']} />
      <div className={styles['container-title']}>{title}</div>
    </a>
  )
}

export default DomainsCard
