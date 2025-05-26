import classNames from 'classnames'

import { Tag, TagProps } from 'design-system/Tag/Tag'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CheckboxAsset.module.scss'

export enum CheckboxAssetVariant {
  ICON = 'icon',
  TAG = 'tag',
  TEXT = 'test',
  IMAGE = 'image',
}

export enum CheckboxAssetImageSizeVariant {
  S = 's',
  M = 'm',
  L = 'l',
}

export type CheckboxAssetProps =
  | {
      variant: CheckboxAssetVariant.ICON
      src: string
      size?: never
      text?: never
      tag?: never
    }
  | {
      variant: CheckboxAssetVariant.TAG
      size?: never
      text?: never
      src?: never
      tag: TagProps
    }
  | {
      variant: CheckboxAssetVariant.TEXT
      text: string
      size?: never
      src?: never
      tag?: never
    }
  | {
      variant: CheckboxAssetVariant.IMAGE
      src: string
      text?: never
      tag?: never
      size?: CheckboxAssetImageSizeVariant
    }

export function CheckboxAsset({
  className,
  variant,
  src,
  size = CheckboxAssetImageSizeVariant.S,
  text,
  tag,
}: { className?: string } & CheckboxAssetProps) {
  if (variant === CheckboxAssetVariant.ICON) {
    return (
      <div className={classNames(styles['icon'], className)}>
        <SvgIcon alt="" src={src} />
      </div>
    )
  }

  if (variant === CheckboxAssetVariant.IMAGE) {
    return (
      <div className={classNames(styles['image'], styles[size], className)}>
        <img src={src} alt="" className={styles['img']} />
      </div>
    )
  }

  if (variant === CheckboxAssetVariant.TEXT) {
    return <div className={classNames(styles['text'], className)}>{text}</div>
  }

  return (
    <div className={classNames(styles['tag'], className)}>
      <Tag {...tag} />
    </div>
  )
}
