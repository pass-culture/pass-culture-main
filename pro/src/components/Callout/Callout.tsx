import cn from 'classnames'
import React from 'react'

import { CalloutVariant } from 'components/Callout/types'
import fullNextIcon from 'icons/full-next.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeErrorIcon from 'icons/stroke-error.svg'
import strokeInfoIcon from 'icons/stroke-info.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import LinkNodes, { Link } from '../../ui-kit/Banners/LinkNodes/LinkNodes'

import styles from './Callout.module.scss'

export interface CalloutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
  title?: string
  links?: Link[]
  closable?: boolean
  onClose?: undefined | (() => void)
  type?: CalloutVariant
  titleOnly?: boolean
}

interface CalloutVariantProps {
  src: string
  alt: string
}

const Callout = ({
  children,
  className,
  title,
  links,
  closable = false,
  onClose,
  type = CalloutVariant.DEFAULT,
  titleOnly = false,
}: CalloutProps): JSX.Element => {
  let calloutIcon: CalloutVariantProps
  /* istanbul ignore next: graphic variations */
  switch (type) {
    case CalloutVariant.WARNING:
      calloutIcon = { src: strokeWarningIcon, alt: 'Attention' }
      break
    case CalloutVariant.SUCCESS:
      calloutIcon = { src: strokeValidIcon, alt: 'Confirmation' }
      break
    case CalloutVariant.ERROR:
      calloutIcon = { src: strokeErrorIcon, alt: 'Erreur' }
      break
    default:
      calloutIcon = { src: strokeInfoIcon, alt: 'Information' }
      break
  }

  const hasNoBottomSpace = (titleOnly || !title) && !links
  return (
    <div
      className={cn(
        styles['callout'],
        styles[`callout-${type}`],
        hasNoBottomSpace ? styles['small-callout'] : '',
        className
      )}
    >
      <SvgIcon
        src={calloutIcon.src}
        alt={calloutIcon.alt}
        className={styles['icon']}
        width="20"
      />
      <div className={styles['content']}>
        {title && <div className={styles['title']}>{title}</div>}
        {!titleOnly && (
          <>
            {children && (
              <div className={styles['callout-text']}>{children}</div>
            )}
            <LinkNodes links={links} defaultLinkIcon={fullNextIcon} />
          </>
        )}
      </div>
      {closable && (
        <button
          onClick={onClose}
          type="button"
          className={styles['close-icon']}
        >
          <SvgIcon src={strokeCloseIcon} alt="Fermer le message" width="20" />
        </button>
      )}
    </div>
  )
}

export default Callout
