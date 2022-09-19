import React, { FunctionComponent, SVGProps } from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './IconLinkBox.module.scss'

export interface IIconLinkBoxProps {
  title: string
  linkTitle: string
  linkUrl: string
  IconHeader: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  IconLink: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}

const IconLinkBox = ({
  title,
  IconHeader,
  IconLink,
  linkTitle,
  linkUrl,
}: IIconLinkBoxProps) => {
  return (
    <div className={styles['icon-link-box']}>
      <div className={styles['icon-link-box-header']}>
        <IconHeader className={styles['icon-link-box-header-icon']} />
        <h2 className={styles['icon-link-box-title']}>{title}</h2>
      </div>
      <div className={styles['icon-link-box-footer']}>
        <div className={styles['icon-link-box-footer-break']} />
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: linkUrl,
            isExternal: true,
          }}
          Icon={IconLink}
          className={styles['icon-link-box-footer-link']}
        >
          {linkTitle}
        </ButtonLink>
      </div>
    </div>
  )
}

export default IconLinkBox
