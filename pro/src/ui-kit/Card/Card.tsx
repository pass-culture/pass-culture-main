import cn from 'classnames'
import type { ReactNode } from 'react'

import styles from './Card.module.scss'

interface CardProps {
  children: ReactNode
  className?: string
  variant?: 'default' | 'info'
}

interface CardHeaderProps {
  title: string
  subtitle?: string
  className?: string
  titleTag?: 'h2' | 'h3' | 'h4'
}

interface CardContentProps {
  children: ReactNode
  className?: string
}

interface CardFooterProps {
  children: ReactNode
  className?: string
}

interface CardImageProps {
  src: string
  alt: string
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

const CardImage = ({ src, alt, className }: CardImageProps) => (
  <img src={src} alt={alt} className={cn(styles['card-image'], className)} />
)

export const Card = ({
  children,
  className,
  variant = 'default',
}: CardProps) => (
  <div
    className={cn(
      styles['card'],
      {
        [styles['card-info']]: variant === 'info',
      },
      className
    )}
  >
    {children}
  </div>
)

Card.Header = CardHeader
Card.Content = CardContent
Card.Footer = CardFooter
Card.Image = CardImage
