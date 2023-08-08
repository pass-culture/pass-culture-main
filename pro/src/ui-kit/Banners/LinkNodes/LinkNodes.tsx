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
}

interface LinkNodesProps {
  links?: Link[]
  defaultLinkIcon?: string
}

const LinkNodes = ({
  defaultLinkIcon = fullLinkIcon,
  links = [],
}: LinkNodesProps): React.ReactNode | React.ReactNode[] => {
  const getLinkNode = (link: Link) => (
    <ButtonLink
      link={{
        isExternal: link.isExternal === undefined ? true : link.isExternal,
        to: link.href,
        target: link.targetLink || '_blank',
        rel: 'noopener noreferrer',
      }}
      icon={link.hideLinkIcon ? undefined : link.icon || defaultLinkIcon}
      className={styles['bi-link']}
      onClick={link.onClick ?? undefined}
    >
      {link.linkTitle}
    </ButtonLink>
  )

  if (links.length > 1) {
    return (
      <ul>
        {links.map(link => {
          return (
            <li key={link.href} className={styles['bi-link-item']}>
              {getLinkNode(link)}
            </li>
          )
        })}
      </ul>
    )
  }

  return links[0] && getLinkNode(links[0])
}

export default LinkNodes
