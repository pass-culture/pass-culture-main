import cn from 'classnames'
import type { ReactNode } from 'react'

import styles from './Card.module.scss'

export interface CardProps {
  children: ReactNode
  className?: string
}

export interface CardHeaderProps {
  title: string
  subtitle?: string
  className?: string
  titleTag?: 'h2' | 'h3' | 'h4'
}

export interface CardContentProps {
  children: ReactNode
  className?: string
}

export interface CardFooterProps {
  children: ReactNode
  className?: string
}

const CardHeader = ({
  title,
  subtitle,
  className,
  titleTag: TitleTag = 'h2',
}: CardHeaderProps) => (
  <div className={cn(styles['card-header'], className)}>
    <TitleTag className={styles['card-title']}>{title}</TitleTag>
    {subtitle && <p className={styles['card-subtitle']}>{subtitle}</p>}
  </div>
)

const CardContent = ({ children, className }: CardContentProps) => (
  <div className={cn(styles['card-content'], className)}>{children}</div>
)

const CardFooter = ({ children, className }: CardFooterProps) => (
  <div className={cn(styles['card-footer'], className)}>{children}</div>
)

export const Card = ({ children, className }: CardProps) => (
  <div className={cn(styles['card'], className)}>{children}</div>
)

Card.Header = CardHeader
Card.Content = CardContent
Card.Footer = CardFooter
