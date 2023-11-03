import cn from 'classnames'
import { useStats } from 'react-instantsearch'
import { NavLink } from 'react-router-dom'

import {
  AdageFrontRoles,
  AdageHeaderLink,
  AuthenticatedResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import strokeBookmarkIcon from 'icons/stroke-bookmark.svg'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import styles from './AdageHeaderMenu.module.scss'

type AdageHeaderMenuProps = {
  adageUser: AuthenticatedResponse
}

export const AdageHeaderMenu = ({ adageUser }: AdageHeaderMenuProps) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  const { favoritesCount } = useAdageUser()

  const { nbHits } = useStats()

  const areFavoritesActive = useActiveFeature('WIP_ENABLE_LIKE_IN_ADAGE')
  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')

  const logAdageLinkClick = (headerLinkName: AdageHeaderLink) => {
    apiAdage.logHeaderLinkClick({
      iframeFrom: removeParamsFromUrl(location.pathname),
      header_link_name: headerLinkName,
    })
  }

  return (
    <ul className={styles['adage-header-menu']}>
      {adageUser.role !== AdageFrontRoles.READONLY && (
        <>
          {isDiscoveryActive && (
            <li className={styles['adage-header-menu-item']}>
              <NavLink
                to={`/adage-iframe/decouverte?token=${adageAuthToken}`}
                end
                className={({ isActive }) => {
                  return cn(styles['adage-header-link'], {
                    [styles['adage-header-link-active']]: isActive,
                  })
                }}
                /*onClick={() => logAdageLinkClick(AdageHeaderLink.DISCOVERY)} */
              >
                <SvgIcon src={strokePassIcon} alt="" width="20" />
                Découvrir
              </NavLink>
            </li>
          )}
          <li className={styles['adage-header-menu-item']}>
            <NavLink
              to={`/adage-iframe?token=${adageAuthToken}`}
              end
              className={({ isActive }) => {
                return cn(styles['adage-header-link'], {
                  [styles['adage-header-link-active']]: isActive,
                })
              }}
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

          {areFavoritesActive && (
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
                  src={strokeBookmarkIcon}
                  alt=""
                  className={styles['adage-header-link-icon']}
                />
                Mes Favoris
                <div className={styles['adage-header-nb-hits']}>
                  {favoritesCount ?? 0}
                </div>
              </NavLink>
            </li>
          )}

          <li className={styles['adage-header-menu-item']}>
            <a
              href={`${document.referrer}adage/passculture/index`}
              className={styles['adage-header-link']}
              target="_parent"
              onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
            >
              <SvgIcon
                alt=""
                src={strokeBookedIcon}
                className={styles['adage-header-link-icon']}
              />
              Suivi
            </a>
          </li>
        </>
      )}
    </ul>
  )
}
