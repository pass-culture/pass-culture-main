import cn from 'classnames'

import styles from './DomainsCard.module.scss'

interface DomainsCardProps {
  title: string
  color: string
  src: string
}

const DomainsCard = ({ title, color, src }: DomainsCardProps) => {
  return (
    <div className={cn(styles['container'], styles[`container-${color}`])}>
      <img src={src} alt="" className={styles['container-img']} />
      <div className={styles['container-title']}>{title}</div>
    </div>
  )
}

export default DomainsCard
