import classnames from 'classnames'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { GET_OFFERER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { hasStatusCode } from 'commons/core/OfferEducational/utils/hasStatusCode'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useIsNewInterfaceActive } from 'commons/hooks/useIsNewInterfaceActive'
import {
  SIDE_NAV_MIN_HEIGHT_COLLAPSE_MEDIA_QUERY,
  useMediaQuery,
} from 'commons/hooks/useMediaQuery'
import {
  setIsCollectiveSectionOpen,
  setIsIndividualSectionOpen,
} from 'commons/store/nav/reducer'
import {
  selectIsCollectiveSectionOpen,
  selectIsIndividualSectionOpen,
} from 'commons/store/nav/selector'
import {
  selectCurrentOffererId,
  selectCurrentUser,
} from 'commons/store/user/selectors'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeCollaboratorIcon from 'icons/stroke-collaborator.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import { getSavedVenueId } from 'pages/Home/Offerers/PartnerPages'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

const INDIVIDUAL_LINKS = ['/offres', '/guichet']
const COLLECTIVE_LINKS = ['/offres/collectives']

export const SideNavLinks = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const isOffererStatsV2Active = useActiveFeature('WIP_OFFERER_STATS_V2')

  const isNewCollectiveOffersStructureEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const currentUser = useSelector(selectCurrentUser)

  const location = useLocation()
  const dispatch = useDispatch()
  const isIndividualSectionOpen = useSelector(selectIsIndividualSectionOpen)
  const isCollectiveSectionOpen = useSelector(selectIsCollectiveSectionOpen)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const sideNavCollapseSize = useMediaQuery(
    SIDE_NAV_MIN_HEIGHT_COLLAPSE_MEDIA_QUERY
  )

  const selectedOffererQuery = useSWR(
    selectedOffererId ? [GET_OFFERER_QUERY_KEY, selectedOffererId] : null,
    async ([, offererId]) => {
      try {
        const offerer = await api.getOfferer(Number(offererId))

        return offerer
      } catch (error) {
        if (hasStatusCode(error) && error.status === HTTP_STATUS.FORBIDDEN) {
          throw error
        }
        return null
      }
    },
    {
      fallbackData: null,
      shouldRetryOnError: false,
      onError: () => {},
    }
  )

  const isUserOffererValidated = !selectedOffererQuery.error

  const selectedOfferer = selectedOffererQuery.data
  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  const venueId =
    getSavedVenueId(selectedOfferer?.managedVenues ?? []) ??
    permanentVenues[0]?.id

  useEffect(() => {
    if (sideNavCollapseSize) {
      dispatch(
        setIsIndividualSectionOpen(INDIVIDUAL_LINKS.includes(location.pathname))
      )
      dispatch(
        setIsCollectiveSectionOpen(COLLECTIVE_LINKS.includes(location.pathname))
      )
    }
  }, [sideNavCollapseSize, dispatch, location.pathname])

  const offererId = localStorageAvailable()
    ? localStorage.getItem(SAVED_OFFERER_ID_KEY)
    : null
  const createOfferPageUrl =
    '/offre/creation' +
    (!isNewInterfaceActive && offererId ? `?structure=${offererId}` : '')

  return (
    <div
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      {selectedOffererQuery.data && isUserOffererValidated && (
        <ul className={styles['nav-links-group']}>
          <li className={styles['nav-links-create-offer-wrapper']}>
            <ButtonLink variant={ButtonVariant.PRIMARY} to={createOfferPageUrl}>
              Créer une offre
            </ButtonLink>
          </li>
        </ul>
      )}
      <ul
        className={classnames(
          styles['nav-links-group'],
          styles['nav-links-scroll']
        )}
      >
        <li>
          <NavLink
            to="/accueil"
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
          <button
            onClick={() => {
              const willOpenIndividualSection = !isIndividualSectionOpen
              if (sideNavCollapseSize && willOpenIndividualSection) {
                dispatch(setIsCollectiveSectionOpen(false))
              }
              dispatch(setIsIndividualSectionOpen(willOpenIndividualSection))
            }}
            className={(styles['nav-links-item'], styles['nav-section-button'])}
            aria-expanded={isIndividualSectionOpen}
            aria-controls="individual-sublist"
            id="individual-sublist-button"
          >
            <SvgIcon src={strokePhoneIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
            <span className={styles['nav-section-title']}>Individuel</span>
            <SvgIcon
              src={isIndividualSectionOpen ? fullUpIcon : fullDownIcon}
              alt=""
              width="18"
              className={styles['nav-section-icon']}
            />
          </button>

          {isIndividualSectionOpen && (
            <ul
              id="individual-sublist"
              aria-labelledby="individual-sublist-button"
            >
              <li>
                <NavLink
                  to="/offres"
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                  end
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Offres
                  </span>
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/reservations"
                  end
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Réservations
                  </span>
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
                  <span className={styles['nav-links-item-without-icon']}>
                    Guichet
                  </span>
                </NavLink>
              </li>
              {currentUser?.hasPartnerPage && venueId && (
                <li>
                  <NavLink
                    to={`/structures/${offererId}/lieux/${venueId}`}
                    className={({ isActive }) =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isActive,
                      })
                    }
                    end
                  >
                    <span className={styles['nav-links-item-without-icon']}>
                      Page sur l’application
                    </span>
                  </NavLink>
                </li>
              )}
            </ul>
          )}
        </li>
        <li>
          <button
            onClick={() => {
              const willdOpenCollectiveSection = !isCollectiveSectionOpen
              if (sideNavCollapseSize && willdOpenCollectiveSection) {
                dispatch(setIsIndividualSectionOpen(false))
              }
              dispatch(
                dispatch(setIsCollectiveSectionOpen(willdOpenCollectiveSection))
              )
            }}
            className={(styles['nav-links-item'], styles['nav-section-button'])}
            aria-expanded={isCollectiveSectionOpen}
            aria-controls="collective-sublist"
            id="collective-sublist-button"
          >
            <SvgIcon
              src={strokeTeacherIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
            />
            <span className={styles['nav-section-title']}>Collectif</span>
            <SvgIcon
              src={isCollectiveSectionOpen ? fullUpIcon : fullDownIcon}
              alt=""
              width="18"
              className={styles['nav-section-icon']}
            />
          </button>
          {isCollectiveSectionOpen && (
            <ul
              id="collective-sublist"
              aria-labelledby="collective-sublist-button"
            >
              {isNewCollectiveOffersStructureEnabled && (
                <li>
                  <NavLink
                    to="/offres/vitrines"
                    className={({ isActive }) =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isActive,
                      })
                    }
                  >
                    <span className={styles['nav-links-item-without-icon']}>
                      Offres vitrines
                    </span>
                  </NavLink>
                </li>
              )}
              <li>
                <NavLink
                  to="/offres/collectives"
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Offres
                  </span>
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/reservations/collectives"
                  end
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Réservations
                  </span>
                </NavLink>
              </li>
              {venueId && (
                <li>
                  <NavLink
                    to={`/structures/${offererId}/lieux/${venueId}/collectif`}
                    className={({ isActive }) =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isActive,
                      })
                    }
                    end
                  >
                    <span className={styles['nav-links-item-without-icon']}>
                      Page dans ADAGE
                    </span>
                  </NavLink>
                </li>
              )}
            </ul>
          )}
        </li>
        {isOffererStatsActive && !isOffererStatsV2Active && (
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
      </ul>
      <ul className={styles['nav-links-group']}>
        <li
          className={styles['nav-links-last-group-separator']}
          aria-hidden="true"
        >
          <div className={styles['separator-line']} />
        </li>
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
        <li>
          <NavLink
            to="/collaborateurs"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon
              src={strokeCollaboratorIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
            />
            Collaborateurs
          </NavLink>
        </li>
      </ul>
    </div>
  )
}
