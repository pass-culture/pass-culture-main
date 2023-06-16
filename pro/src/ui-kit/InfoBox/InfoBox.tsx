import cn from 'classnames'
import React, { ReactNode } from 'react'

import { ReactComponent as FullLink } from 'icons/full-link.svg'
import TipsHelpIcon from 'icons/shadow-tips_help.svg'
import { ButtonLink } from 'ui-kit/Button'
import type { LinkProps } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InfoBox.module.scss'

interface InfoBoxLinkProps extends LinkProps {
  text: string
}

export interface InfoBoxProps {
  children: ReactNode
  link?: InfoBoxLinkProps
}

const InfoBox = ({ children, link }: InfoBoxProps): JSX.Element => {
  return (
    <div className={cn(styles['info-box'])}>
      <div className={styles['info-box-header']}>
        <div className={cn(styles['info-box-bar'])} />
        <div className={styles['info-box-title']}>
          <SvgIcon
            src={TipsHelpIcon}
            alt=""
            className={styles['info-box-title-icon']}
            viewBox="0 0 24 26"
          />
          <span>À SAVOIR</span>
        </div>
        <div className={cn(styles['info-box-bar'])} />
      </div>

      <p className={styles['info-box-text']}>{children}</p>

      {link && (
        <ButtonLink
          link={link}
          Icon={FullLink}
          className={styles['info-box-link']}
        >
          {link.text}
        </ButtonLink>
      )}
    </div>
  )
}

export default InfoBox
