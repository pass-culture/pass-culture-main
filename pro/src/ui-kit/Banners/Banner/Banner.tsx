import React, { FunctionComponent, SVGProps } from 'react'

import { ReactComponent as FullLink } from 'icons/full-link.svg'
import styles from 'ui-kit/Banners/BannerLayout/BannerLayout.module.scss'
import { ButtonLink } from 'ui-kit/Button'

import BannerLayout from '../BannerLayout'
import { BannerLayoutProps } from '../BannerLayout/BannerLayout'

export type Link = {
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  href: string
  linkTitle: string
  targetLink?: string
  hideLinkIcon?: boolean
  isExternal?: boolean
}
export interface IBannerProps extends BannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  links?: Link[]
}

const Banner = ({
  children,
  links = [],
  ...bannerLayoutProps
}: IBannerProps): JSX.Element => {
  /* istanbul ignore next: DEBT to fix */
  const getLinkNode = (link: Link) => (
    /* istanbul ignore next: DEBT to fix */
    <ButtonLink
      link={{
        isExternal: link.isExternal === undefined ? true : link.isExternal,
        to: link.href,
        target: link.targetLink || '_blank',
        rel: 'noopener noreferrer',
      }}
      Icon={
        /* istanbul ignore next: DEBT to fix */
        link.hideLinkIcon ? undefined : link.Icon || FullLink
      }
      className={styles['bi-link']}
    >
      {link.linkTitle}
    </ButtonLink>
  )

  const getLinksNode = () => {
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

  return (
    <BannerLayout linkNode={getLinksNode()} {...bannerLayoutProps}>
      {children}
    </BannerLayout>
  )
}

export default Banner
