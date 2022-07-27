import cn from 'classnames'
import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'
import { ReactComponent as PassCultureSvg } from 'icons/ico-passculture.svg'
import { ReactComponent as TagSvg } from 'icons/ico-tag.svg'

import style from './OptionsIcons.module.scss'

interface IOptionsIconsProps {
  isEvent: boolean
  isDuo: boolean
  className?: string
}

const OptionsIcons = ({
  isEvent,
  isDuo,
  className,
}: IOptionsIconsProps): JSX.Element => {
  return (
    <div className={cn(className, style['options-container'])}>
      <div className={style['option']}>
        <PassCultureSvg aria-hidden className={style['icon']} />
        <span className={style['text']}>Type</span>
      </div>
      <div
        className={cn(style['option'], {
          [style['disabled']]: !(isEvent && isDuo),
        })}
      >
        <DuoSvg aria-hidden className={style['icon']} />
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
