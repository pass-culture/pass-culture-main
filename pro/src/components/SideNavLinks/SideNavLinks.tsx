import classnames from 'classnames'
import React from 'react'
import { NavLink } from 'react-router-dom'

import useActiveFeature from 'hooks/useActiveFeature'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import deskIcon from 'icons/stroke-desk.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'
const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

const SideNavLinks = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  return (
    <ul
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      <div className={styles['nav-links-first-group']}>
        <li>
          <NavLink
            to={'/accueil'}
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon src={strokeHomeIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
            <span className={styles['nav-links-item-title']}>Accueil</span>
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/guichet"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon src={deskIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
            Guichet
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/offres"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon src={strokeOffersIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
            Offres
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/reservations"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon
              alt=""
              src={strokeCalendarIcon}
              width={NAV_ITEM_ICON_SIZE}
            />
            Réservations
          </NavLink>
        </li>

        {isOffererStatsActive && (
          <li>
            <NavLink
              to="/statistiques"
              className={({ isActive }) =>
                classnames(styles['nav-links-item'], {
                  [styles['nav-links-item-active']]: isActive,
                })
              }
            >
              <SvgIcon src={strokePieIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
              Statistiques
            </NavLink>
          </li>
        )}
      </div>
      <div className={styles['nav-links-last-group']}>
        <div className={styles['nav-links-last-group-separator']} />
        <li>
          <NavLink
            to="/remboursements"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon src={strokeEuroIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
            Gestion financière
          </NavLink>
        </li>
      </div>
    </ul>
  )
}

export default SideNavLinks
