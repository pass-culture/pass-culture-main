import cn from 'classnames'
import { useStats } from 'react-instantsearch'
import { NavLink } from 'react-router-dom'

import {
  AdageFrontRoles,
  AdageHeaderLink,
  AuthenticatedResponse,
} from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageHeaderMenu.module.scss'

type AdageHeaderMenuProps = {
  adageUser: AuthenticatedResponse
  logAdageLinkClick: (link: AdageHeaderLink) => void
}

export const AdageHeaderMenu = ({
  adageUser,
  logAdageLinkClick,
}: AdageHeaderMenuProps) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  const { favoritesCount } = useAdageUser()

  const { nbHits } = useStats()

  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')

  return (
    <ul className={styles['adage-header-menu']}>
      {adageUser.role !== AdageFrontRoles.READONLY && (
        <>
          {isDiscoveryActive && (
            <li className={styles['adage-header-menu-item']}>
              <NavLink
                to={`/adage-iframe?token=${adageAuthToken}`}
                end
                className={({ isActive }) => {
                  return cn(styles['adage-header-link'], {
                    [styles['adage-header-link-active']]: isActive,
                  })
                }}
                onClick={() => logAdageLinkClick(AdageHeaderLink.DISCOVERY)}
              >
                <SvgIcon src={strokePassIcon} alt="" width="20" />
                Découvrir
              </NavLink>
            </li>
          )}
          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe/recherche?token=${adageAuthToken}`}
              end
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
              //  TODO : rework the facet filters + the formik context on the search page so that the search state can be
              //  safely resetted based on the page url, and so that the facet filters are managed inside the router.
              reloadDocument
              onClick={() => logAdageLinkClick(AdageHeaderLink.SEARCH)}
            >
              <SvgIcon src={strokeSearchIcon} alt="" width="20" />
              Rechercher
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
              <SvgIcon
                src={strokeVenueIcon}
                alt=""
                className={styles['adage-header-link-icon']}
              />
              Pour mon établissement
              <div className={styles['adage-header-nb-hits']}>{nbHits}</div>
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
              <SvgIcon
                src={strokeStarIcon}
                alt=""
                className={styles['adage-header-link-icon']}
              />
              Mes Favoris
              <div className={styles['adage-header-nb-hits']}>
                {favoritesCount ?? 0}
              </div>
            </NavLink>
          </li>
        </>
      )}
    </ul>
  )
}
