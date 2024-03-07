import classnames from 'classnames'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, useLocation } from 'react-router-dom'

import { SAVED_OFFERER_ID_KEY } from 'core/shared'
import useActiveFeature from 'hooks/useActiveFeature'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import {
  setIsCollectiveSectionOpen,
  setIsIndividualSectionOpen,
} from 'store/nav/reducer'
import {
  selectIsCollectiveSectionOpen,
  selectIsIndividualSectionOpen,
} from 'store/nav/selector'
import { ButtonLink } from 'ui-kit'
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

const SideNavLinks = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const location = useLocation()
  const dispatch = useDispatch()
  const isIndividualSectionOpen = useSelector(selectIsIndividualSectionOpen)
  const isCollectiveSectionOpen = useSelector(selectIsCollectiveSectionOpen)

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
    '/offre/creation' + (offererId ? `?structure=${offererId}` : '')

  return (
    <ul
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      <div className={styles['nav-links-first-group']}>
        <li className={styles['nav-links-create-offer-wrapper']}>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{ isExternal: false, to: createOfferPageUrl }}
          >
            Créer une offre
          </ButtonLink>
        </li>
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
          <button
            onClick={() =>
              dispatch(setIsIndividualSectionOpen(!isIndividualSectionOpen))
            }
            className={(styles['nav-links-item'], styles['nav-section-button'])}
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
            <>
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
            </>
          )}
        </li>
        <li>
          <button
            onClick={() =>
              dispatch(setIsCollectiveSectionOpen(!isCollectiveSectionOpen))
            }
            className={(styles['nav-links-item'], styles['nav-section-button'])}
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
            <>
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
            </>
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
