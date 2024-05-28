import rightIcon from 'icons/stroke-right.svg'
import { ButtonLink, ButtonLinkProps } from 'ui-kit/Button/ButtonLink'
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
                <ButtonLink
                  link={{
                    ...crumb.link,
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
