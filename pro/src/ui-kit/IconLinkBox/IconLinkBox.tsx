import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './IconLinkBox.module.scss'

export interface IconLinkBoxProps {
  title: string
  linkTitle: string
  linkUrl: string
  iconHeader: string
  iconLink: string
  onClick?: () => void
}

const IconLinkBox = ({
  title,
  iconHeader,
  iconLink,
  linkTitle,
  linkUrl,
  onClick,
}: IconLinkBoxProps) => {
  return (
    <div className={styles['icon-link-box']}>
      <div className={styles['icon-link-box-header']}>
        <SvgIcon
          src={iconHeader}
          alt=""
          className={styles['icon-link-box-header-icon']}
        />
        <h2 className={styles['icon-link-box-title']}>{title}</h2>
      </div>
      <div className={styles['icon-link-box-footer']}>
        <div className={styles['icon-link-box-footer-break']} />
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: linkUrl,
            isExternal: false,
          }}
          onClick={onClick}
          icon={iconLink}
          className={styles['icon-link-box-footer-link']}
        >
          {linkTitle}
        </ButtonLink>
      </div>
    </div>
  )
}

export default IconLinkBox
