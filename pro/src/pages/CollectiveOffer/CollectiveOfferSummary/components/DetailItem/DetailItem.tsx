import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './DetailItem.module.scss'

type DetailItemProps = {
  children: React.ReactNode
  src?: string
  alt?: string
}

export const DetailItem = ({ children, src, alt }: DetailItemProps) => (
  <div className={styles['definition-item']}>
    {src && (
      <dt>
        <SvgIcon className={styles['icon']} alt={alt} src={src} />
      </dt>
    )}
    <dd>{children}</dd>
  </div>
)
