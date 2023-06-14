import cn from 'classnames'
import React from 'react'

import { PasscultureIcon } from 'icons'
import { ReactComponent as TagSvg } from 'icons/ico-tag.svg'
import strokeDuoIcon from 'icons/stroke-duo.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import style from './OptionsIcons.module.scss'

interface OptionsIconsProps {
  isEvent: boolean
  isDuo: boolean
  className?: string
}

const OptionsIcons = ({
  isEvent,
  isDuo,
  className,
}: OptionsIconsProps): JSX.Element => {
  return (
    <div className={cn(className, style['options-container'])}>
      <div className={style['option']}>
        <PasscultureIcon
          aria-hidden
          className={cn(style['icon'], style['passculture'])}
        />
        <span className={style['text']}>Type</span>
      </div>

      <div
        className={cn(style['option'], {
          [style['disabled']]: !(isEvent && isDuo),
        })}
      >
        <SvgIcon src={strokeDuoIcon} alt="" className={style['icon']} />
        <span className={style['text']}>À deux !</span>
      </div>

      <div className={style['option']}>
        <TagSvg aria-hidden className={style['icon']} />
        <span className={style['text']}>- - €</span>
      </div>
    </div>
  )
}

export default OptionsIcons
