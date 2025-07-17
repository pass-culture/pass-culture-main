import cn from 'classnames'

import fullErrorIcon from 'icons/full-error.svg'
import fullInfoIcon from 'icons/full-info.svg'
import fullValidIcon from 'icons/full-validate.svg'
import fullWarningIcon from 'icons/full-warning.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Link, LinkNodes } from 'ui-kit/LinkNodes/LinkNodes'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Callout.module.scss'

export interface CalloutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
  title?: string
  links?: Link[]
  closable?: boolean
  onClose?: undefined | (() => void)
  variant?: CalloutVariant
  testId?: string
  shouldShowIcon?: boolean
}

interface CalloutVariantProps {
  src: string
  alt: string
}

export const Callout = ({
  children,
  className,
  title,
  links,
  closable = false,
  onClose,
  testId,
  variant = CalloutVariant.INFO,
  shouldShowIcon = true,
}: CalloutProps): JSX.Element => {
  let calloutIcon: CalloutVariantProps
  /* istanbul ignore next: graphic variations */
  switch (variant) {
    case CalloutVariant.WARNING:
      calloutIcon = { src: fullWarningIcon, alt: 'Attention' }
      break
    case CalloutVariant.SUCCESS:
      calloutIcon = { src: fullValidIcon, alt: 'Confirmation' }
      break
    case CalloutVariant.ERROR:
      calloutIcon = { src: fullErrorIcon, alt: 'Erreur' }
      break
    case CalloutVariant.INFO:
      calloutIcon = { src: fullInfoIcon, alt: 'Information' }
      break
  }

  const hasNoBottomSpace = !links
  return (
    <div
      className={cn(
        styles['callout'],
        styles[`callout-${variant}`],
        hasNoBottomSpace ? styles['small-callout'] : '',
        className
      )}
      data-testid={testId}
    >
      {shouldShowIcon && (
        <SvgIcon
          src={calloutIcon.src}
          alt={calloutIcon.alt}
          className={styles['icon']}
          width="20"
        />
      )}
      <div className={styles['content']}>
        {title && <div className={styles['title']}>{title}</div>}
        {children && <div className={styles['callout-text']}>{children}</div>}
        {links && <LinkNodes links={links} />}
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
