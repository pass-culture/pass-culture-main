import React, { FunctionComponent, SVGProps } from 'react'

import { ReactComponent as ExternalSiteIcon } from 'icons/ico-external-site-filled.svg'
import { ButtonLink } from 'ui-kit/Button'

import BannerLayout from '../BannerLayout'
import { IBannerLayoutProps } from '../BannerLayout/BannerLayout'
import styles from '../BannerLayout/BannerLayout.module.scss'

type Link = {
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  href: string
  linkTitle: string
  targetLink?: string
  hideLinkIcon?: boolean
}
export interface IBannerProps extends IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  links?: Link[]
}

const Banner = ({
  children,
  links = [],
  ...bannerLayoutProps
}: IBannerProps): JSX.Element => {
  const getLinkNode = (link: Link) => (
    <ButtonLink
      link={{
        isExternal: true,
        to: link.href,
        target: link.targetLink || '_blank',
        rel: 'noopener noreferrer',
      }}
      Icon={link.hideLinkIcon ? undefined : link.Icon || ExternalSiteIcon}
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
