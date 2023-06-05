import cn from 'classnames'
import React, { ReactNode } from 'react'

import { ReactComponent as BulbIcon } from 'icons/ico-bulb.svg'
import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { ButtonLink } from 'ui-kit/Button'
import type { LinkProps } from 'ui-kit/Button/ButtonLink'

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
          <BulbIcon className={styles['info-box-title-icon']} />
          <span>À SAVOIR</span>
        </div>
        <div className={cn(styles['info-box-bar'])} />
      </div>

      <p className={styles['info-box-text']}>{children}</p>

      {link && (
        <ButtonLink
          link={link}
          Icon={LinkIcon}
          className={styles['info-box-link']}
        >
          {link.text}
        </ButtonLink>
      )}
    </div>
  )
}

export default InfoBox
