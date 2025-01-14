import cn from 'classnames'
import { Link } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CardLink.module.scss'

interface CardLinkProps {
  className?: string
  to: string
  icon?: string
  label: string
  accessibleLabel?: string
  description?: string
  accessibleDescription?: string
  direction?: 'horizontal' | 'vertical'
}

export const CardLink = ({
  className,
  to,
  icon,
  label,
  accessibleLabel = label,
  description,
  accessibleDescription = description,
  direction = 'horizontal',
}: CardLinkProps): JSX.Element => {
  return (
    <Link
      to={to}
      className={cn(
        styles['cardlink'],
        direction === 'vertical' && styles['vertical'],
        className
      )}
    >
      <div className={styles['cardlink-body']}>
        <div className={styles['cardlink-content']}>
          <p>
            <span className={styles['visually-hidden']}>
              {accessibleLabel}.
            </span>
            <span aria-hidden>{label}</span>
          </p>

          {description && (
            <>
              <p className={styles['visually-hidden']}>
                {accessibleDescription}.
              </p>
              <p className={styles['cardlink-description']} aria-hidden>
                {description}
              </p>
            </>
          )}
        </div>
        {icon && (
          <SvgIcon src={icon} className={styles['cardlink-icon']} alt="" />
        )}
      </div>
    </Link>
  )
}
