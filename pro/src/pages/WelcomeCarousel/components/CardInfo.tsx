import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CardInfo.module.scss'

type CardInfoProps = {
  icon: string
  title: string
  titleLevel?: '2' | '3'
  description: string
}
export const CardInfo = ({
  icon,
  title,
  titleLevel = '3',
  description,
}: CardInfoProps): JSX.Element => {
  const Heading = `h${titleLevel}` satisfies React.ElementType

  return (
    <div className={styles['card-info']}>
      <div className={styles['card-info-header']}>
        <div className={styles['card-info-icon-wrapper']}>
          <SvgIcon src={icon} className={styles['card-info-icon']} />
        </div>
        <Heading className={styles['card-info-header-title']}>{title}</Heading>
      </div>

      <p className={styles['card-info-description']}>{description}</p>
    </div>
  )
}
