import classNames from 'classnames'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

interface IconProps {
  icon: string
  iconAlt?: string
  className?: string
  iconClassName?: string
  width: number
}

export const Icon = ({
  icon,
  iconAlt,
  className,
  iconClassName,
  width,
}: Readonly<IconProps>) => {
  return (
    <SvgIcon
      src={icon}
      alt={iconAlt}
      className={classNames(className, iconClassName)}
      //  width={width}
    />
  )
}
