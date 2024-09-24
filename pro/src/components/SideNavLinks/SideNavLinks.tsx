import classnames from 'classnames'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { GET_OFFERER_QUERY_KEY } from 'config/swrQueryKeys'
import { hasStatusCode } from 'core/OfferEducational/utils/hasStatusCode'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeCollaboratorIcon from 'icons/stroke-collaborator.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import { getSavedVenueId } from 'pages/Home/Offerers/PartnerPages'
import {
  setIsCollectiveSectionOpen,
  setIsIndividualSectionOpen,
} from 'store/nav/reducer'
import {
  selectIsCollectiveSectionOpen,
  selectIsIndividualSectionOpen,
} from 'store/nav/selector'
import { selectCurrentOffererId, selectCurrentUser } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import styles from './SideNavLinks.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

const INDIVIDUAL_LINKS = ['/offres', '/guichet']
const COLLECTIVE_LINKS = ['/offres/collectives']

export const SideNavLinks = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const { t } = useTranslation('common')
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
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
    if (INDIVIDUAL_LINKS.includes(location.pathname)) {
      dispatch(setIsIndividualSectionOpen(true))
    } else if (COLLECTIVE_LINKS.includes(location.pathname)) {
      dispatch(setIsCollectiveSectionOpen(true))
    }
  }, [dispatch, location.pathname])

  const offererId = localStorageAvailable()
    ? localStorage.getItem(SAVED_OFFERER_ID_KEY)
    : null
  const createOfferPageUrl =
    '/offre/creation' +
    (!isNewInterfaceActive && offererId ? `?structure=${offererId}` : '')

  return (
    <ul
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      {selectedOffererQuery.data && isUserOffererValidated && (
        <li className={styles['nav-links-create-offer-wrapper']}>
          <ButtonLink variant={ButtonVariant.PRIMARY} to={createOfferPageUrl}>
            {t('create_offer')}
          </ButtonLink>
        </li>
      )}
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
          <span className={styles['nav-links-item-title']}>{t('home')}</span>
        </NavLink>
      </li>
      <li>
        <button
          onClick={() =>
            dispatch(setIsIndividualSectionOpen(!isIndividualSectionOpen))
          }
          className={(styles['nav-links-item'], styles['nav-section-button'])}
          aria-expanded={isIndividualSectionOpen}
          aria-controls="individual-sublist"
          id="individual-sublist-button"
        >
          <SvgIcon src={strokePhoneIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
          <span className={styles['nav-section-title']}>{t('individual')}</span>
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
                  {t('offers')}
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
                  {t('reservations')}
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
                  {t('ticket_office')}
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
          onClick={() =>
            dispatch(setIsCollectiveSectionOpen(!isCollectiveSectionOpen))
          }
          className={(styles['nav-links-item'], styles['nav-section-button'])}
          aria-expanded={isCollectiveSectionOpen}
          aria-controls="collective-sublist"
          id="collective-sublist-button"
        >
          <SvgIcon src={strokeTeacherIcon} alt="" width={NAV_ITEM_ICON_SIZE} />
          <span className={styles['nav-section-title']}>{t('collective')}</span>
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
                  {t('offers')}
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
                  {t('reservations')}
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
                    {t('adage_page')}
                  </span>
                </NavLink>
              </li>
            )}
          </ul>
        )}
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
            {t('statistics')}
          </NavLink>
        </li>
      )}
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
          {t('financial_management')}
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
          {t('collaborators')}
        </NavLink>
      </li>
    </ul>
  )
}
