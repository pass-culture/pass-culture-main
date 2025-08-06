import classnames from 'classnames'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import fullGoTop from '@/icons/full-go-top.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BackToNavLink.module.scss'

interface BackToNavLinkProps {
  className?: string
}

export const BackToNavLink = ({
  className,
}: BackToNavLinkProps): JSX.Element => {
  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

  return (
    <a
      id="back-to-nav-link"
      href={isMobileScreen ? '#header-nav-toggle' : '#lateral-panel'}
      className={classnames(className, styles['back-to-nav-link'])}
    >
      <SvgIcon
        src={fullGoTop}
        alt="Revenir à la barre de navigation"
        width="20"
      />
    </a>
  )
}
