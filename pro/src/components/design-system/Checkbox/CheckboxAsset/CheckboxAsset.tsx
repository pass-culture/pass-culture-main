import classNames from 'classnames'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CheckboxAsset.module.scss'

export type CheckboxAssetImageSizeVariant = 'S' | 'M' | 'L'

export type CheckboxAssetProps =
  | {
      variant: 'icon'
      src: string
      size?: never
      text?: never
    }
  | { variant: 'tag'; size?: never; text?: never; src?: never }
  | { variant: 'text'; text: string; size?: never; src?: never }
  | {
      variant: 'image'
      src: string
      text?: never
      size?: CheckboxAssetImageSizeVariant
    }

export function CheckboxAsset({
  className,
  variant,
  src,
  size = 'S',
  text,
}: { className?: string } & CheckboxAssetProps) {
  if (variant === 'icon') {
    return (
      <div className={classNames(styles['icon'], className)}>
        <SvgIcon alt="" src={src} />
      </div>
    )
  }

  if (variant === 'image') {
    return (
      <div
        className={classNames(
          styles['image'],
          { [styles[size]]: size },
          className
        )}
      >
        <img src={src} alt="" className={styles['img']} />
      </div>
    )
  }

  if (variant === 'text') {
    return <div className={classNames(styles['text'], className)}>{text}</div>
  }

  //  TODO : use the new Tag
  return
}
