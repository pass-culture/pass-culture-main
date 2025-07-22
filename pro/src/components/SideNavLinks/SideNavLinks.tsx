import classnames from 'classnames'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, useLocation } from 'react-router'

import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
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
  selectSelectedPartnerPageId,
} from 'commons/store/nav/selector'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { getSavedPartnerPageVenueId } from 'commons/utils/savedPartnerPageVenueId'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeCollaboratorIcon from 'icons/stroke-collaborator.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
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
  const isNewCollectiveOffersStructureEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const location = useLocation()
  const dispatch = useDispatch()
  const isIndividualSectionOpen = useSelector(selectIsIndividualSectionOpen)
  const isCollectiveSectionOpen = useSelector(selectIsCollectiveSectionOpen)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const sideNavCollapseSize = useMediaQuery(
    SIDE_NAV_MIN_HEIGHT_COLLAPSE_MEDIA_QUERY
  )

  const { data: selectedOfferer, error: offererApiError } = useOfferer(
    selectedOffererId,
    true
  )
  const isUserOffererValidated = !offererApiError

  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []
  const hasPartnerPageVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.hasPartnerPage) ??
    []
  const venueId = permanentVenues[0]?.id

  const reduxStoredPartnerPageId = useSelector(selectSelectedPartnerPageId)
  const savedPartnerPageVenueId = getSavedPartnerPageVenueId(
    'partnerPage',
    selectedOffererId
  )
  const stillRelevantSavedPartnerPageVenueId = hasPartnerPageVenues
    .find((venue) => venue.id.toString() === savedPartnerPageVenueId)
    ?.id.toString()

  // At first, redux store is empty. We check local storage and use
  // first partner page venue as defautl if local storage is empty too.
  // If local storage changes from VenueEdition, we update redux store
  // as well - and use the new selectedPartnerPageVenueId here.
  const selectedPartnerPageVenueId =
    reduxStoredPartnerPageId ||
    stillRelevantSavedPartnerPageVenueId ||
    hasPartnerPageVenues[0]?.id

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

  return (
    <div
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      {selectedOfferer && isUserOffererValidated && (
        <ul className={styles['nav-links-group']}>
          <li className={styles['nav-links-create-offer-wrapper']}>
            <ButtonLink variant={ButtonVariant.PRIMARY} to={'/offre/creation'}>
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
            <SvgIcon
              src={strokeHomeIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles['icon']}
            />
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
            <SvgIcon
              src={strokePhoneIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles['icon']}
            />
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
              {selectedPartnerPageVenueId && (
                <li>
                  <NavLink
                    to={`/structures/${selectedOffererId}/lieux/${selectedPartnerPageVenueId}/page-partenaire`}
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
              className={styles['icon']}
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
                    to={`/structures/${selectedOffererId}/lieux/${venueId}/collectif`}
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
            <SvgIcon
              src={strokeEuroIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles['icon']}
            />
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
              className={styles['icon']}
            />
            Collaborateurs
          </NavLink>
        </li>
      </ul>
    </div>
  )
}
