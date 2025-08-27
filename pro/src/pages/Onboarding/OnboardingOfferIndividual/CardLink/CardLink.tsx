import cn from 'classnames'
import { Link } from 'react-router'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CardLink.module.scss'

export type CardLinkProps = {
  className?: string
  icon?: string
  label: string
  description?: string
  direction?: 'horizontal' | 'vertical'
  to?: string
  onClick?: () => void
} & (
  | {
      to: string
    }
  | { onClick: () => void }
)

export const CardLink = ({
  className,
  to,
  icon,
  label,
  description,
  direction = 'horizontal',
  onClick,
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
            {to && (
              <Link to={to} className={cn(styles['cardlink-link'])}>
                {label}
              </Link>
            )}

            {onClick && (
              <button
                type="button"
                className={cn(styles['cardlink-button'])}
                onClick={onClick}
              >
                {label}
              </button>
            )}
          </p>

          {description && (
            <p className={styles['cardlink-description']}>{description}</p>
          )}
        </div>
      </div>
    </div>
  )
}
