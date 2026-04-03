import { Card } from '@/ui-kit/Card/Card'

import styles from './EditoCardItem.module.scss'

type EditoCardItemProps = {
  image: string
  title: string
  subtitle: string
  footer: React.ReactNode
}

export const EditoCardItem = ({
  image,
  title,
  subtitle,
  footer,
}: EditoCardItemProps) => (
  <Card className={styles['edito-card']}>
    <Card.Image src={image} alt="" className={styles['edito-card-image']} />
    <Card.Header
      title={title}
      titleTag="h3"
      subtitle={subtitle}
      titleClassName={styles['edito-card-title']}
      subtitleClassName={styles['edito-card-subtitle']}
    />
    <Card.Footer className={styles['edito-card-footer']}>{footer}</Card.Footer>
  </Card>
)
