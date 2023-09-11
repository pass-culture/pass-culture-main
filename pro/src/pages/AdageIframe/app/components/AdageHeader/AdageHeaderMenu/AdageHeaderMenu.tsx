import cn from 'classnames'
import { NavLink } from 'react-router-dom'

import {
  AdageFrontRoles,
  AdageHeaderLink,
  AuthenticatedResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import styles from './AdageHeaderMenu.module.scss'

type AdageHeaderMenuProps = {
  adageUser: AuthenticatedResponse
  institutionsOfferCount: number
}

export const AdageHeaderMenu = ({
  adageUser,
  institutionsOfferCount,
}: AdageHeaderMenuProps) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  const { favoriteCount } = useAdageUser()

  const areFavoritesActive = useActiveFeature('WIP_ENABLE_LIKE_IN_ADAGE')

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
          <li>
            <NavLink
              to={`/adage-iframe?token=${adageAuthToken}`}
              end
              className={({ isActive }) => {
                return cn(styles['adage-header-item'], {
                  [styles['adage-header-item-active']]: isActive,
                })
              }}
              onClick={() => logAdageLinkClick(AdageHeaderLink.SEARCH)}
            >
              <SvgIcon src={strokeSearchIcon} alt="" width="20" />
              Rechercher
            </NavLink>
          </li>
          <li>
            <NavLink
              to={`/adage-iframe/mon-etablissement?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-item'], {
                  [styles['adage-header-item-active']]: isActive,
                })
              }}
              onClick={() =>
                logAdageLinkClick(AdageHeaderLink.MY_INSTITUTION_OFFERS)
              }
            >
              <SvgIcon
                src={strokeVenueIcon}
                alt=""
                className={styles['adage-header-item-icon']}
              />
              Pour mon établissement
              <div className={styles['adage-header-nb-hits']}>
                {institutionsOfferCount}
              </div>
            </NavLink>
          </li>

          {areFavoritesActive && (
            <li>
              <NavLink
                to={`/adage-iframe/mes-favoris?token=${adageAuthToken}`}
                className={({ isActive }) => {
                  return cn(styles['adage-header-item'], {
                    [styles['adage-header-item-active']]: isActive,
                  })
                }}
                onClick={() => logAdageLinkClick(AdageHeaderLink.MY_FAVORITES)}
              >
                <SvgIcon
                  src={strokeVenueIcon}
                  alt=""
                  className={styles['adage-header-item-icon']}
                />
                Mes Favoris
                <div className={styles['adage-header-nb-hits']}>
                  {favoriteCount}
                </div>
              </NavLink>
            </li>
          )}

          <li>
            <a
              href={`${document.referrer}adage/passculture/index`}
              className={styles['adage-header-item']}
              target="_parent"
              onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
            >
              <SvgIcon
                alt=""
                src={strokeBookedIcon}
                className={styles['adage-header-item-icon']}
              />
              Suivi
            </a>
          </li>
        </>
      )}
    </ul>
  )
}
