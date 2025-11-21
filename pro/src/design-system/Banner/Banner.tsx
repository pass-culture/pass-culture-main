import cx from 'classnames'

import closeIcon from '@/icons/full-close.svg'
import infosIcon from '@/icons/full-info.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Banner.module.scss'

export enum BannerVariants {
  DEFAULT = 'default',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
}

export type BannerLink = {
  label: string
  href: string
  isExternal?: boolean
  icon?: string
  iconAlt?: string
  /** Action type (e.g. "link", "button") */
  type: 'link' | 'button'
  onClick?: () => void
}

export type BannerProps = {
  title: string
  description?: string | JSX.Element
  actions?: BannerLink[]
  icon?: string
  imageSrc?: string
  /** Visual style (defines colors) */
  variant?: BannerVariants
  size?: 'default' | 'large'
  /** Show close button? */
  closable?: boolean
  /** Callback called on close button click */
  onClose?: () => void
}

export const Banner = ({
  title,
  description,
  actions = [],
  icon = infosIcon,
  imageSrc,
  variant = BannerVariants.DEFAULT,
  size = 'default',
  closable = false,
  onClose,
}: BannerProps): JSX.Element => {
  return (
    <div className={cx(styles.banner, styles[variant])} data-testid="banner">
      <div className={styles.inner}>
        <div className={styles.content}>
          <SvgIcon className={styles.info} src={icon} aria-hidden="true" />

          <div
            className={cx(styles['content-body'], {
              [styles['content-body-large']]: size === 'large',
            })}
          >
            <span
              className={cx(styles['title'], {
                [styles['title-large']]: size === 'large',
              })}
            >
              {title}
            </span>
            {description && (
              <span className={styles.description}>{description}</span>
            )}
            {actions.length > 0 && (
              <ul className={styles['actions-list']}>
                {actions.map((a) => (
                  <li key={a.label}>
                    {a.type === 'link' ? (
                      <ButtonLink
                        className={cx(styles.link, {
                          [styles['link-large']]: size === 'large',
                        })}
                        href={a.href}
                        target={a.isExternal ? '_blank' : '_self'}
                        rel={a.isExternal ? 'noopener noreferrer' : undefined}
                        to={a.href}
                        icon={a.icon}
                        iconAlt={a.iconAlt}
                        isExternal={a.isExternal}
                      >
                        {a.label}
                      </ButtonLink>
                    ) : (
                      <Button
                        className={cx(styles.link, {
                          [styles['link-large']]: size === 'large',
                        })}
                        variant={ButtonVariant.TERNARY}
                        icon={a.icon}
                        onClick={() => a.onClick?.()}
                      >
                        {a.label}
                      </Button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
          {imageSrc && (
            <img
              src={imageSrc}
              className={styles.image}
              alt=""
              aria-hidden="true"
            />
          )}
          {closable && (
            <button
              type="button"
              className={styles['close-button']}
              onClick={onClose}
              aria-label="Fermer la bannière d’information"
            >
              <SvgIcon src={closeIcon} width="16" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
