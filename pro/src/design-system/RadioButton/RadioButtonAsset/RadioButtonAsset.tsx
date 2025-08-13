import classNames from 'classnames'

import { Tag, type TagProps } from '@/design-system/Tag/Tag'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButtonAsset.module.scss'

export type RadioButtonAssetProps =
  | {
      variant: 'icon'
      src: string
      size?: never
      text?: never
      tag?: never
    }
  | {
      variant: 'tag'
      size?: never
      text?: never
      src?: never
      tag: TagProps
    }
  | {
      variant: 'text'
      text: string
      size?: never
      src?: never
      tag?: never
    }
  | {
      variant: 'image'
      src: string
      text?: never
      tag?: never
      size?: 's' | 'm' | 'l'
    }

export function RadioButtonAsset({
  className,
  variant,
  src,
  size = 's',
  text,
  tag,
}: { className?: string } & RadioButtonAssetProps) {
  if (variant === 'icon') {
    return (
      <div className={classNames(styles['icon'], className)}>
        <SvgIcon alt="" src={src} />
      </div>
    )
  }

  if (variant === 'image') {
    return (
      <div className={classNames(styles['image'], styles[size], className)}>
        <img src={src} alt="" className={styles['img']} />
      </div>
    )
  }

  if (variant === 'text') {
    return <div className={classNames(styles['text'], className)}>{text}</div>
  }

  return (
    <div className={classNames(styles['tag'], className)}>
      <Tag {...tag} />
    </div>
  )
}
