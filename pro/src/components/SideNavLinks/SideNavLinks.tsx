/** biome-ignore-all lint/correctness/useUniqueElementIds: SideNavLinks is used once per page. There cannot be id duplications. */
import classnames from 'classnames'
import { useEffect } from 'react'
import { NavLink, useLocation } from 'react-router'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  SIDE_NAV_MIN_HEIGHT_COLLAPSE_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { setOpenSection } from '@/commons/store/nav/reducer'
import {
  openSection,
  selectSelectedPartnerPageId,
} from '@/commons/store/nav/selector'
import { getSavedPartnerPageVenueId } from '@/commons/utils/savedPartnerPageVenueId'
import fullDownIcon from '@/icons/full-down.svg'
import fullLeftIcon from '@/icons/full-left.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import strokeHomeIcon from '@/icons/stroke-home.svg'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { EllipsissedText } from '../EllipsissedText/EllipsissedText'
import styles from './SideNavLinks.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

const INDIVIDUAL_LINKS = [
  /offres$/,
  /reservations$/,
  /guichet$/,
  /structures\/\d+\/lieux\/\d+\/page-partenaire/,
]
const COLLECTIVE_LINKS = [
  /offres\/collectives$/,
  /reservations\/collectives$/,
  /structures\/\d+\/lieux\/\d+\/collectif/,
]

const matches = (patterns: RegExp[], path: string) =>
  patterns.some((rx) => rx.test(path))

export const SideNavLinks = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const location = useLocation()

  const dispatch = useAppDispatch()
  const navOpenSection = useAppSelector(openSection)
  const selectedOfferer = useAppSelector(
    (state) => state.offerer.currentOfferer
  )
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)
  const sideNavCollapseSize = useMediaQuery(
    SIDE_NAV_MIN_HEIGHT_COLLAPSE_MEDIA_QUERY
  )
  const isCaledonian = useIsCaledonian()

  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.isPermanent) ?? []
  const hasPartnerPageVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.hasPartnerPage) ?? []
  const venueId = withSwitchVenueFeature
    ? selectedVenue?.id
    : permanentVenues[0]?.id

  // Keep: this makes the “resize → auto-collapse to matching section” work.
  // biome-ignore lint/correctness/useExhaustiveDependencies: We do not want the changes if the state changes
  useEffect(() => {
    if (!sideNavCollapseSize) {
      return
    }

    const path = location.pathname
    const openIndividual = matches(INDIVIDUAL_LINKS, path)
    const openCollective = matches(COLLECTIVE_LINKS, path)

    // Only dispatch if a change is actually needed
    if (
      openIndividual !== navOpenSection.individual ||
      openCollective !== navOpenSection.collective
    ) {
      dispatch(
        setOpenSection({
          individual:
            openIndividual !== navOpenSection.individual
              ? openIndividual
              : navOpenSection.individual,
          collective:
            openCollective !== navOpenSection.collective
              ? openCollective
              : navOpenSection.collective,
        })
      )
    }
  }, [sideNavCollapseSize, location.pathname, dispatch])

  const reduxStoredPartnerPageId = useAppSelector(selectSelectedPartnerPageId)
  const savedPartnerPageVenueId = getSavedPartnerPageVenueId(
    'partnerPage',
    selectedOfferer?.id
  )
  const stillRelevantSavedPartnerPageVenueId = hasPartnerPageVenues
    .find((v) => v.id.toString() === savedPartnerPageVenueId)
    ?.id.toString()

  const selectedPartnerPageVenueId =
    reduxStoredPartnerPageId ||
    stillRelevantSavedPartnerPageVenueId ||
    hasPartnerPageVenues.at(0)?.id

  return (
    <div
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-with-padding-top']]: !withSwitchVenueFeature,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      {selectedOfferer && (
        <div className={styles['nav-links-group']}>
          {withSwitchVenueFeature && selectedVenue && (
            <ButtonLink
              aria-label={`Changer de structure (actuellement sélectionnée : ${selectedVenue.name})`}
              className={styles['nav-links-switch-venue-button']}
              icon={fullLeftIcon}
              isIconAriaHidden
              to="/hub"
            >
              <EllipsissedText>{selectedVenue.name}</EllipsissedText>
            </ButtonLink>
          )}

          <div className={styles['nav-links-create-offer-wrapper']}>
            <DropdownButton
              name="Créer une offre"
              triggerProps={{
                className: styles['nav-links-create-offer-wrapper-trigger'],
              }}
              options={[
                {
                  element: (
                    <ButtonLink
                      to={getIndividualOfferUrl({
                        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                        mode: OFFER_WIZARD_MODE.CREATION,
                        isOnboarding: false,
                      })}
                      icon={strokePhoneIcon}
                    >
                      Pour le grand public
                    </ButtonLink>
                  ),
                  id: 'individual',
                },
                {
                  element: (
                    <ButtonLink to="/offre/creation" icon={strokeBagIcon}>
                      Pour les groupes scolaires
                    </ButtonLink>
                  ),
                  id: 'collective',
                },
              ]}
            />
          </div>
        </div>
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
              className={styles.icon}
            />
            <span className={styles['nav-links-item-title']}>Accueil</span>
          </NavLink>
        </li>

        {/* INDIVIDUEL */}
        <li>
          <button
            type="button"
            onClick={() => {
              const willOpen = !navOpenSection.individual

              dispatch(
                setOpenSection({
                  individual: willOpen,
                  collective:
                    sideNavCollapseSize && willOpen
                      ? false
                      : navOpenSection.collective,
                })
              )
            }}
            className={classnames(
              styles['nav-links-item'],
              styles['nav-section-button']
            )}
            aria-expanded={navOpenSection.individual}
            aria-controls="individual-sublist"
            id="individual-sublist-button"
          >
            <SvgIcon
              src={strokePhoneIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles.icon}
            />
            <span className={styles['nav-section-title']}>Individuel</span>
            <SvgIcon
              src={navOpenSection.individual ? fullUpIcon : fullDownIcon}
              alt=""
              width="18"
              className={styles['nav-section-icon']}
            />
          </button>

          {navOpenSection.individual && (
            <ul
              id="individual-sublist"
              aria-labelledby="individual-sublist-button"
            >
              <li>
                <NavLink
                  to="/offres"
                  end
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
              {selectedOfferer && selectedPartnerPageVenueId && (
                <li>
                  <NavLink
                    to={`/structures/${selectedOfferer.id}/lieux/${selectedPartnerPageVenueId}/page-partenaire`}
                    end
                    className={({ isActive }) =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isActive,
                      })
                    }
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

        {/* COLLECTIF */}
        <li>
          <button
            type="button"
            onClick={() => {
              const willOpen = !navOpenSection.collective

              dispatch(
                setOpenSection({
                  individual:
                    sideNavCollapseSize && willOpen
                      ? false
                      : navOpenSection.individual,
                  collective: willOpen,
                })
              )
            }}
            className={classnames(
              styles['nav-links-item'],
              styles['nav-section-button']
            )}
            aria-expanded={navOpenSection.collective}
            aria-controls="collective-sublist"
            id="collective-sublist-button"
          >
            <SvgIcon
              src={strokeTeacherIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles.icon}
            />
            <span className={styles['nav-section-title']}>Collectif</span>
            <SvgIcon
              src={navOpenSection.collective ? fullUpIcon : fullDownIcon}
              alt=""
              width="18"
              className={styles['nav-section-icon']}
            />
          </button>

          {navOpenSection.collective && (
            <ul
              id="collective-sublist"
              aria-labelledby="collective-sublist-button"
            >
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
                    Offres réservables
                  </span>
                </NavLink>
              </li>

              {selectedOfferer && venueId && (
                <li>
                  <NavLink
                    to={`/structures/${selectedOfferer.id}/lieux/${venueId}/collectif`}
                    end
                    className={({ isActive }) =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isActive,
                      })
                    }
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

      <div className={styles['nav-links-group']}>
        <div
          className={styles['nav-links-last-group-separator']}
          aria-hidden="true"
        >
          <div className={styles['separator-line']} />
        </div>
        <div>
          <NavLink
            to="/remboursements"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon
              src={isCaledonian ? strokeFrancIcon : strokeEuroIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles.icon}
            />
            Gestion financière
          </NavLink>
        </div>
        <div>
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
              className={styles.icon}
            />
            Collaborateurs
          </NavLink>
        </div>
      </div>
    </div>
  )
}
