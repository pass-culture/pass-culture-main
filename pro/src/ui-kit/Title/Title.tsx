import type { theme } from '@pass-culture/design-system/lib/pro/light.web'
import cn from 'classnames'

import styles from './Title.module.scss'

type DSSpacing = keyof typeof theme.size.spacing

type TitleProps = Omit<
  React.HTMLAttributes<HTMLHeadingElement>,
  'className'
> & {
  level: '1' | '2' | '3' | '4'
  title: string
  marginTop?: DSSpacing
  marginBottom?: DSSpacing
}

const toSpacing = (spacing: DSSpacing | undefined): string =>
  spacing ? `var(--size-spacing-${spacing})` : '0'

export const Title = ({
  level,
  title,
  marginTop,
  marginBottom,
  ...props
}: Readonly<TitleProps>): JSX.Element => {
  const Heading = `h${level}` satisfies React.ElementType

  return (
    <Heading
      className={cn(styles['title'], styles[`title-${level}`])}
      style={
        {
          '--title-margin-top': toSpacing(marginTop),
          '--title-margin-bottom': toSpacing(marginBottom),
        } as React.CSSProperties
      }
      {...props}
    >
      {title}
    </Heading>
  )
}
