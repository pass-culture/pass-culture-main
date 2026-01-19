import classNames from 'classnames'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

interface IconProps {
  icon: string
  iconAlt?: string
  className?: string
  iconClassName?: string
}

export const Icon = ({
  icon,
  iconAlt,
  className,
  iconClassName,
}: Readonly<IconProps>) => {
  return (
    <SvgIcon
      src={icon}
      alt={iconAlt}
      className={classNames(className, iconClassName)}
      width={'16'}
    />
  )
}
