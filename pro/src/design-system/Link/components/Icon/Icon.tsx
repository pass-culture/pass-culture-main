import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

interface IconProps {
  icon: string
  className?: string
  iconAlt?: string
}

export const Icon = ({ icon, className, iconAlt }: Readonly<IconProps>) => {
  return <SvgIcon src={icon} alt={iconAlt} className={className} />
}
