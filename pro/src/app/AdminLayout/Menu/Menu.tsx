import cn from 'classnames'
import { matchPath, NavLink, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { ReactComponent as IconDesk } from 'icons/ico-desk.svg'
import { ReactComponent as IconEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IconHome } from 'icons/ico-home.svg'

import styles from './Menu.module.scss'

interface IMenuProps {
  className?: string
}

const Menu = ({ className }: IMenuProps) => {
  const { currentUser } = useCurrentUser()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const isSelected = {
    accueil: !!matchPath(location.pathname, { path: '/accueil' }),
    structures: !!matchPath(location.pathname, { path: '/structures' }),
    guichet: !!matchPath(location.pathname, { path: '/guichet' }),
    remboursements: !!matchPath(location.pathname, {
      path: '/remboursements/justificatifs',
    }),
  }

  return (
    <nav className={cn(className, styles['menu'])}>
      <NavLink
        className={cn(styles['nav-item'], {
          [styles['selected']]: isSelected.accueil || isSelected.structures,
        })}
        onClick={() => {
          logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
        }}
        role="menuitem"
        to={currentUser.isAdmin ? '/structures' : '/accueil'}
      >
        <IconHome aria-hidden className={styles['nav-item-icon']} />
        Accueil
      </NavLink>

      <NavLink
        className={cn(styles['nav-item'], {
          [styles['selected']]: isSelected.guichet,
        })}
        onClick={() => {
          logEvent?.(Events.CLICKED_TICKET, { from: location.pathname })
        }}
        role="menuitem"
        to="/guichet"
      >
        <IconDesk aria-hidden className={styles['nav-item-icon']} />
        Guichet
      </NavLink>

      <NavLink
        className={cn(styles['nav-item'], {
          [styles['selected']]: isSelected.remboursements,
        })}
        onClick={() => {
          logEvent?.(Events.CLICKED_REIMBURSEMENT, {
            from: location.pathname,
          })
        }}
        role="menuitem"
        to="/remboursements/justificatifs"
      >
        <IconEuro aria-hidden className={styles['nav-item-icon']} />
        Remboursements
      </NavLink>
    </nav>
  )
}

export default Menu
