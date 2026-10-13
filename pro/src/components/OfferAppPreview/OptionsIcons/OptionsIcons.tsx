import cn from 'classnames'

import strokeDuoIcon from '@/icons/stroke-duo.svg'
import strokePassIcon from '@/icons/stroke-pass.svg'
import strokePriceIcon from '@/icons/stroke-price.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import style from './OptionsIcons.module.scss'

interface OptionsIconsProps {
  isEvent: boolean
  isDuo: boolean
  className?: string
}

export const OptionsIcons = ({
  isEvent,
  isDuo,
  className,
}: OptionsIconsProps): JSX.Element => {
  return (
    <div className={cn(className, style['options-container'])}>
      <div className={style['option']}>
        <SvgIcon src={strokePassIcon} alt="" className={style['icon']} />
        <p className={style['text']}>Type</p>
      </div>

      {isEvent && isDuo && (
        <div className={style['option']}>
          <SvgIcon src={strokeDuoIcon} alt="" className={style['icon']} />
          <p className={style['text']}>À deux !</p>
        </div>
      )}
      <div className={style['option']}>
        <SvgIcon src={strokePriceIcon} alt="" className={style['icon']} />
        <p className={style['text']}>- - €</p>
      </div>
    </div>
  )
}
