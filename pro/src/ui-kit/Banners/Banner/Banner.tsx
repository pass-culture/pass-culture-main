import React, { FunctionComponent, SVGProps } from 'react'

import { ReactComponent as ExternalSiteIcon } from 'icons/ico-external-site-filled.svg'
import oldStyles from 'ui-kit/Banners/BannerLayout/BannerLayout.module.scss'
import newStyles from 'ui-kit/Banners/BannerLayout/NewBannerLayout.module.scss'
import { ButtonLink } from 'ui-kit/Button'

import BannerLayout from '../BannerLayout'
import { IBannerLayoutProps } from '../BannerLayout/BannerLayout'

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
export interface IBannerProps extends IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  links?: Link[]
}

const Banner = ({
  children,
  links = [],
  ...bannerLayoutProps
}: IBannerProps): JSX.Element => {
  const isNewStyles = true
  /* istanbul ignore next: DEBT to fix */
  const styles = isNewStyles ? newStyles : oldStyles
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
        link.hideLinkIcon ? undefined : link.Icon || ExternalSiteIcon
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
