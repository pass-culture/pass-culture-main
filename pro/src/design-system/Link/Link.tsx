import classNames from 'classnames'
import { forwardRef } from 'react'
import { Link as RouterLink } from 'react-router'

import fullLinkIcon from '@/icons/full-link.svg'

import { Icon } from './components/Icon/Icon'
import styles from './Link.module.scss'
import { LinkColor, type LinkProps, LinkSize } from './types'

export const Link = forwardRef<HTMLAnchorElement, Readonly<LinkProps>>(
  (
    {
      label,
      to,
      icon,
      onClick,
      color = LinkColor.BRAND,
      isExternalLink = false,
      shouldOpenNewTab = false,
      size = LinkSize.DEFAULT,
    },
    ref
  ): JSX.Element => {
    const className = classNames(
      styles.link,
      styles[`link-${size}`],
      styles[`link-${color}`]
    )

    const labelElement = <span className={styles['link-label']}>{label}</span>

    if (isExternalLink) {
      return (
        <a
          ref={ref}
          href={to}
          className={className}
          onClick={onClick}
          rel="noopener noreferrer"
          target={shouldOpenNewTab ? '_blank' : undefined}
        >
          {(icon || shouldOpenNewTab) && (
            <Icon
              icon={icon || fullLinkIcon}
              className={styles['link-icon']}
              iconAlt={shouldOpenNewTab ? 'Nouvelle fenêtre' : ''}
            />
          )}
          {labelElement}
        </a>
      )
    }

    return (
      <RouterLink
        ref={ref}
        to={to}
        className={className}
        onClick={onClick}
        target={shouldOpenNewTab ? '_blank' : undefined}
      >
        {(icon || shouldOpenNewTab) && (
          <Icon
            icon={icon || fullLinkIcon}
            className={styles['link-icon']}
            iconAlt={shouldOpenNewTab ? 'Nouvelle fenêtre' : ''}
          />
        )}
        {labelElement}
      </RouterLink>
    )
  }
)

Link.displayName = 'Link'
