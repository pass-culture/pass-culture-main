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
  title: string
  links?: Link[]
  closable?: boolean
  onClose?: undefined | (() => void)
  type?: CalloutVariant
}

const Callout = ({
  children,
  className,
  title,
  links,
  closable = false,
  onClose,
  type = CalloutVariant.DEFAULT,
}: CalloutProps): JSX.Element => {
  let calloutIconSrc
  /* istanbul ignore next: graphic variations */
  switch (type) {
    case CalloutVariant.WARNING:
      calloutIconSrc = strokeWarningIcon
      break
    case CalloutVariant.SUCCESS:
      calloutIconSrc = strokeValidIcon
      break
    case CalloutVariant.ERROR:
      calloutIconSrc = strokeErrorIcon
      break
    default:
      calloutIconSrc = strokeInfoIcon
      break
  }
  return (
    <div
      className={cn(styles['callout'], className, styles[`callout-${type}`])}
    >
      <SvgIcon
        src={calloutIconSrc}
        alt=""
        className={styles['icon']}
        width="24"
      />
      <div className={styles['content']}>
        <div className={styles['title']}>{title}</div>
        {children && <div className={styles['callout-text']}>{children}</div>}
        <LinkNodes links={links} defaultLinkIcon={fullNextIcon} />
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
