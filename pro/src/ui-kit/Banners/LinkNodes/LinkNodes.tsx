import React from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button'

import styles from './LinkNodes.module.scss'

export type Link = {
  icon?: string
  href: string
  linkTitle: string
  targetLink?: string
  hideLinkIcon?: boolean
  isExternal?: boolean
  onClick?: () => void
  svgAlt?: string
  'aria-label'?: string
}

interface LinkNodeProps {
  link: Link
  defaultLinkIcon?: string
}

interface LinkNodesProps {
  links?: Link[]
  defaultLinkIcon?: string
}

const LinkNode = ({
  link: {
    icon,
    href,
    linkTitle,
    targetLink = '_blank',
    hideLinkIcon,
    isExternal = true,
    onClick,
    svgAlt,
    'aria-label': ariaLabel,
  },
  defaultLinkIcon = fullLinkIcon,
}: LinkNodeProps): React.ReactNode => (
  <ButtonLink
    link={{
      isExternal: isExternal,
      to: href,
      target: targetLink,
      rel: 'noopener noreferrer',
      'aria-label': ariaLabel,
    }}
    icon={hideLinkIcon ? undefined : icon ?? defaultLinkIcon}
    className={styles['bi-link']}
    onClick={onClick}
    svgAlt={svgAlt}
  >
    {linkTitle}
  </ButtonLink>
)

const LinkNodes = ({
  defaultLinkIcon,
  links = [],
}: LinkNodesProps): React.ReactNode | React.ReactNode[] => {
  if (links.length > 1) {
    return (
      <ul>
        {links.map((link) => {
          return (
            <li key={link.href} className={styles['bi-link-item']}>
              <LinkNode link={link} defaultLinkIcon={defaultLinkIcon} />
            </li>
          )
        })}
      </ul>
    )
  }

  return (
    links[0] && <LinkNode link={links[0]} defaultLinkIcon={defaultLinkIcon} />
  )
}

export default LinkNodes
