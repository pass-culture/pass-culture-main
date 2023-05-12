import cn from 'classnames'
import React from 'react'

import { ReactComponent as AttentionIcon } from 'icons/ico-attention.svg'
import { ReactComponent as BulbIcon } from 'icons/ico-bulb.svg'
import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { ButtonLink } from 'ui-kit/Button'
import type { LinkProps } from 'ui-kit/Button/ButtonLink'

import styles from './InfoBox.module.scss'

interface InfoBoxLinkProps extends LinkProps {
  text: string
}

export interface InfoBoxProps {
  type: 'info' | 'important'
  text: string
  link?: InfoBoxLinkProps
}

const InfoBox = ({ type, text, link }: InfoBoxProps): JSX.Element => {
  return (
    <div className={cn(styles['info-box'], styles[type])}>
      <div className={styles['info-box-header']}>
        <div className={cn(styles['info-box-bar'])} />
        <div className={styles['info-box-title']}>
          {type === 'info' ? (
            <>
              <BulbIcon className={styles['info-box-title-icon']} />
              <span>À SAVOIR</span>
            </>
          ) : (
            <>
              <AttentionIcon className={styles['info-box-title-icon']} />
              <span>IMPORTANT</span>
            </>
          )}
        </div>
        <div className={cn(styles['info-box-bar'], styles[type])} />
      </div>
      <p className={styles['info-box-text']}>{text}</p>
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
