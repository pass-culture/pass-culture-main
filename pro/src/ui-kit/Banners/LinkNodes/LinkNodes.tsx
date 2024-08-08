import React from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink, LinkProps } from 'ui-kit/Button/ButtonLink'

import styles from './LinkNodes.module.scss'

export type Link = {
  icon?: {
    src: string
    alt: string
  } | null
  href: string
  label: string
  target?: string
  isExternal?: boolean
  onClick?: () => void
  'aria-label'?: string
}

interface LinkNodesProps {
  links?: Link[]
}

export const LinkNode = ({
  icon,
  href,
  label,
  isExternal,
  onClick,
  'aria-label': ariaLabel,
}: Link): React.ReactNode => {
  const forwardLink: LinkProps = { to: href, isExternal }
  if (ariaLabel) {
    forwardLink['aria-label'] = ariaLabel
  }
  return (
    <ButtonLink
      {...forwardLink}
      //  If the link is external, the link automatically opens in a new tab
      opensInNewTab={isExternal}
      icon={isExternal ? fullLinkIcon : (icon?.src ?? fullNextIcon)}
      className={styles['bi-link']}
      onClick={onClick}
    >
      {label}
    </ButtonLink>
  )
}

export const LinkNodes = ({
  links = [],
}: LinkNodesProps): React.ReactNode | React.ReactNode[] => {
  if (links.length > 1) {
    return (
      <ul>
        {links.map((link) => {
          return (
            <li key={link.href} className={styles['bi-link-item']}>
              <LinkNode {...link} />
            </li>
          )
        })}
      </ul>
    )
  }
  return links[0] && <LinkNode {...links[0]} />
}
