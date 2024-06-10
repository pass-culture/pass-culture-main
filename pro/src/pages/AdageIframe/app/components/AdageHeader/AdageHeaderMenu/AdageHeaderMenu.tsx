import cn from 'classnames'
import { NavLink } from 'react-router-dom'

import { AdageFrontRoles, AdageHeaderLink } from 'apiClient/adage'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageHeaderMenu.module.scss'

type AdageHeaderMenuProps = {
  logAdageLinkClick: (link: AdageHeaderLink) => void
}

export const AdageHeaderMenu = ({
  logAdageLinkClick,
}: AdageHeaderMenuProps) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  const {
    favoritesCount,
    institutionOfferCount,
    adageUser: { role },
  } = useAdageUser()

  return (
    <ul className={styles['adage-header-menu']}>
      {role !== AdageFrontRoles.READONLY && (
        <>
          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe/decouverte?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
              onClick={() => logAdageLinkClick(AdageHeaderLink.DISCOVERY)}
            >
              {({ isActive }) => (
                <div className={styles['adage-header-link-focus']}>
                  <SvgIcon src={strokePassIcon} alt="" width="20" />
                  Découvrir
                  <span className={styles['active-link-visually-hidden']}>
                    {isActive ? ' (Onglet actif)' : null}
                  </span>
                </div>
              )}
            </NavLink>
          </li>
          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe/recherche?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
              onClick={() => logAdageLinkClick(AdageHeaderLink.SEARCH)}
            >
              {({ isActive }) => (
                <div className={styles['adage-header-link-focus']}>
                  <SvgIcon src={strokeSearchIcon} alt="" width="20" />
                  Rechercher
                  <span className={styles['active-link-visually-hidden']}>
                    {isActive ? ' (Onglet actif)' : null}
                  </span>
                </div>
              )}
            </NavLink>
          </li>
          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe/mon-etablissement?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
              onClick={() =>
                logAdageLinkClick(AdageHeaderLink.MY_INSTITUTION_OFFERS)
              }
            >
              {({ isActive }) => (
                <div className={styles['adage-header-link-focus']}>
                  <SvgIcon
                    src={strokeVenueIcon}
                    alt=""
                    className={styles['adage-header-link-icon']}
                    width="20"
                  />
                  Pour mon établissement
                  <span className={styles['active-link-visually-hidden']}>
                    {isActive ? ' (Onglet actif)' : null}
                  </span>
                  <div className={styles['adage-header-nb-hits']}>
                    {institutionOfferCount ?? 0}
                  </div>
                </div>
              )}
            </NavLink>
          </li>

          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe/mes-favoris?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
              onClick={() => logAdageLinkClick(AdageHeaderLink.MY_FAVORITES)}
            >
              {({ isActive }) => (
                <div className={styles['adage-header-link-focus']}>
                  <SvgIcon
                    src={strokeStarIcon}
                    alt=""
                    className={styles['adage-header-link-icon']}
                    width="20"
                  />
                  Mes Favoris
                  <span className={styles['active-link-visually-hidden']}>
                    {isActive ? ' (Onglet actif)' : null}
                  </span>
                  <div className={styles['adage-header-nb-hits']}>
                    {favoritesCount ?? 0}
                  </div>
                </div>
              )}
            </NavLink>
          </li>
        </>
      )}
    </ul>
  )
}
