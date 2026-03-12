import cn from 'classnames'
import type { ReactNode } from 'react'

import { Panel } from '@/ui-kit/Panel/Panel'

import styles from './HomeCard.module.scss'

interface HomeCardProps {
  children: ReactNode
  className?: string
}

interface HomeCardHeaderProps {
  title: string
  subtitle?: string
  className?: string
  titleTag?: 'h2' | 'h3' | 'h4'
}

interface HomeCardContentProps {
  children: ReactNode
  className?: string
}

interface HomeCardFooterProps {
  children: ReactNode
  className?: string
}

const HomeCardHeader = ({
  title,
  subtitle,
  className,
  titleTag: TitleTag = 'h3',
}: HomeCardHeaderProps) => (
  <header className={cn(styles['home-card-header'], className)}>
    <TitleTag className={styles['home-card-title']}>{title}</TitleTag>
    {subtitle && <p className={styles['home-card-subtitle']}>{subtitle}</p>}
  </header>
)

const HomeCardContent = ({ children, className }: HomeCardContentProps) => (
  <div className={cn(styles['home-card-content'], className)}>{children}</div>
)

const HomeCardFooter = ({ children, className }: HomeCardFooterProps) => (
  <div className={cn(styles['home-card-footer'], className)}>{children}</div>
)

export const HomeCard = ({ children, className }: HomeCardProps) => (
  <Panel>
    <div className={cn(styles['home-card'], className)}>{children}</div>
  </Panel>
)

HomeCard.Header = HomeCardHeader
HomeCard.Content = HomeCardContent
HomeCard.Footer = HomeCardFooter
