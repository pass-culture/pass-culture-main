import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import rightIcon from '@/icons/stroke-right.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Breadcrumb.module.scss'

export type Crumb = {
  title: string
  link: { to: string; isExternal: boolean }
  icon?: string
}

type BreadcrumbProps = {
  crumbs: Crumb[]
}

export const Breadcrumb = ({ crumbs }: BreadcrumbProps) => {
  return (
    <nav aria-label="Vous êtes ici:" className={styles['breadcrumb']}>
      <ol className={styles['breadcrumb-list']}>
        {crumbs.map((crumb, i) => {
          const isLast = i === crumbs.length - 1
          return (
            <li className={styles['breadcrumb-list-item']} key={crumb.link.to}>
              {isLast ? (
                <span className={styles['breadcrumb-list-last']}>
                  {crumb.title}
                </span>
              ) : (
                <Button
                  as="a"
                  {...crumb.link}
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.BRAND}
                  icon={crumb.icon}
                  label={crumb.title}
                />
              )}
              {!isLast && (
                <SvgIcon
                  alt=""
                  width="12"
                  src={rightIcon}
                  className={styles['breadcrumb-list-item-arrow']}
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
