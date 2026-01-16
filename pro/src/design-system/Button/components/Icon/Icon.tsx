import classNames from 'classnames'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { ButtonSize } from '../../types'
import { ICON_WIDTH } from '../../utils/constants'

interface IconProps {
  icon: string
  iconAlt?: string
  className?: string
  iconClassName?: string
  size?: ButtonSize
}

export const Icon = ({
  icon,
  iconAlt,
  className,
  iconClassName,
  size = ButtonSize.DEFAULT,
}: Readonly<IconProps>) => {
  return (
    <SvgIcon
      src={icon}
      alt={iconAlt}
      className={classNames(className, iconClassName)}
      width={ICON_WIDTH[size]}
    />
  )
}
