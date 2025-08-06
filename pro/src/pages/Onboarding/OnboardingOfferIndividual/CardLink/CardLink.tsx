import cn from 'classnames'
import { Link } from 'react-router'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CardLink.module.scss'

export interface CardLinkProps {
  className?: string
  to: string
  icon?: string
  label: string
  description?: string
  direction?: 'horizontal' | 'vertical'
}

export const CardLink = ({
  className,
  to,
  icon,
  label,
  description,
  direction = 'horizontal',
}: CardLinkProps): JSX.Element => {
  return (
    <div
      className={cn(
        styles['cardlink'],
        direction === 'vertical' && styles['cardlink-vertical'],
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
            <Link to={to} className={cn(styles['cardlink-link'])}>
              {label}
            </Link>
          </p>

          {description && (
            <p className={styles['cardlink-description']}>{description}</p>
          )}
        </div>
      </div>
    </div>
  )
}
