import cn from 'classnames'
import { Link } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CardLink.module.scss'

export interface CardLinkProps {
  className?: string
  to: string
  icon?: string
  label: string
  description?: string
  direction?: 'horizontal' | 'vertical'
  disabled?: boolean
  error?: string
}

export const CardLink = ({
  className,
  to,
  icon,
  label,
  description,
  direction = 'horizontal',
  disabled = false,
  error,
}: CardLinkProps): JSX.Element => {
  return (
    <div
      className={cn(
        styles['cardlink'],
        direction === 'vertical' && styles['cardlink-vertical'],
        disabled && styles['cardlink-disabled'],
        !!error && styles['cardlink-error'],
        className
      )}
      data-testid="cardlink"
    >
      <div className={styles['cardlink-body']}>
        {icon && (
          <SvgIcon src={icon} className={styles['cardlink-icon']} alt="" />
        )}
        <div className={styles['cardlink-content']}>
          <p>
            <Link
              to={to}
              className={cn(
                styles['cardlink-link'],
                disabled && styles['cardlink-link-disabled']
              )}
              aria-disabled={disabled}
            >
              {label}
            </Link>
          </p>

          {description && (
            <p className={styles['cardlink-description']}>{description}</p>
          )}
        </div>
        {error && <p className={styles['cardlink-error-message']}>{error}</p>}
      </div>
    </div>
  )
}
