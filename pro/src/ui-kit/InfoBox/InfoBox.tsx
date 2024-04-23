import cn from 'classnames'
import React, { ReactNode } from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import shadowTipsHelpIcon from 'icons/shadow-tips-help.svg'
import { ButtonLink, type LinkProps } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InfoBox.module.scss'

interface InfoBoxLinkProps extends LinkProps {
  text: string
}

interface InfoBoxProps {
  children: ReactNode
  link?: InfoBoxLinkProps
  svgAlt?: string
}

const InfoBox = ({ children, link, svgAlt }: InfoBoxProps): JSX.Element => {
  return (
    <div className={cn(styles['info-box'])}>
      <div className={styles['info-box-header']}>
        <div className={cn(styles['info-box-bar'])} />
        <div className={styles['info-box-title']}>
          <SvgIcon
            src={shadowTipsHelpIcon}
            alt=""
            className={styles['info-box-title-icon']}
          />
          <span>À SAVOIR</span>
        </div>
        <div className={cn(styles['info-box-bar'])} />
      </div>

      <p className={styles['info-box-text']}>{children}</p>

      {link && (
        <ButtonLink
          link={link}
          icon={fullLinkIcon}
          className={styles['info-box-link']}
          svgAlt={svgAlt || ''}
        >
          {link.text}
        </ButtonLink>
      )}
    </div>
  )
}

export default InfoBox
