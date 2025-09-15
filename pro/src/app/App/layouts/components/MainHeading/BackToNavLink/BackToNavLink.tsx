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
    // biome-ignore lint/correctness/useUniqueElementIds: This is always rendered once per page, so there cannot be id duplications.
    <a
      id="back-to-nav-link"
      aria-label="Revenir à la barre de navigation"
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
