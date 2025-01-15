import classnames from 'classnames'

import fullGoTop from 'icons/full-go-top.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BackToNavLink.module.scss'

interface BackToNavLinkProps {
  isMobileScreen?: boolean
  className?: string
}

export const BackToNavLink = ({
  isMobileScreen,
  className,
}: BackToNavLinkProps): JSX.Element => {
  return (
    <a
      id="back-to-nav-link"
      href={isMobileScreen ? '#header-nav-toggle' : '#lateral-panel'}
      className={classnames(
        className,
        styles['back-to-nav-link']
      )}
    >
      <SvgIcon
        src={fullGoTop}
        alt="Revenir à la barre de navigation"
        width="20"
      />
    </a>
  )
}