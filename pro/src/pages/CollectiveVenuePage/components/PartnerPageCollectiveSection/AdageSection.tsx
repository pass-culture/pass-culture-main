import { Tag, type TagVariant } from '@/design-system/Tag/Tag'

import styles from './AdageSection.module.scss'

interface AdageSectionProps {
  children?: React.ReactNode
  variant: TagVariant
  tagText: string
  description?: React.ReactNode
}
export const AdageSection = ({
  children,
  tagText,
  variant,
  description,
}: Readonly<AdageSectionProps>) => {
  return (
    <section className={styles['details']}>
      <div>
        <span className={styles['details-normal']}>
          État auprès des enseignants&nbsp;:
        </span>
        <div className={styles['tag']}>
          <Tag label={tagText} variant={variant} />
        </div>
      </div>
      {description && (
        <div className={styles['details-description']}>{description}</div>
      )}
      {children}
    </section>
  )
}
