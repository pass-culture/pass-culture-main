import rightIcon from 'icons/stroke-right.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonLinkProps } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Breadcrumb.module.scss'

export type Crumb = {
  title: string
  link: ButtonLinkProps['link']
  icon?: string
}

type BreadcrumbProps = {
  crumbs: Crumb[]
}

export default function Breadcrumb({ crumbs }: BreadcrumbProps) {
  return (
    <nav aria-label="Fil d'ariane" className={styles['breadcrumb']}>
      <ol className={styles['breadcrumb-list']}>
        {crumbs.map((crumb, i) => {
          const isLast = i === crumbs.length - 1
          return (
            <li className={styles['breadcrumb-list-item']} key={crumb.link.to}>
              <ButtonLink
                link={{
                  ...crumb.link,
                  'aria-current': isLast ? 'page' : undefined,
                }}
                className={styles['breadcrumb-list-item-link']}
                variant={ButtonVariant.QUATERNARYPINK}
              >
                <>
                  {crumb.icon && (
                    <SvgIcon
                      src={crumb.icon}
                      alt=""
                      width="16"
                      className={styles['breadcrumb-list-item-link-icon']}
                    />
                  )}
                  {crumb.title}
                </>
              </ButtonLink>
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
