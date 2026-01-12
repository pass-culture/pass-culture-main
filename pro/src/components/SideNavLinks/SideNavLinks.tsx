/** biome-ignore-all lint/correctness/useUniqueElementIds: SideNavLinks is used once per page. There cannot be id duplications. */

import classnames from 'classnames'
import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { UserReviewDialog } from '@/app/App/layouts/components/Header/components/UserReviewDialog/UserReviewDialog'
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
import fullLeftIcon from '@/icons/full-left.svg'
import fullSmsIcon from '@/icons/full-sms.svg'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import strokeHomeIcon from '@/icons/stroke-home.svg'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'

import { EllipsissedText } from '../EllipsissedText/EllipsissedText'
import { HubPageNavigation } from '../HubPageNavigation/HubPageNavigation'
import { HelpDropdownNavItem } from './HelpDropdownNavItem'
import { SideNavLink } from './SideNavLink'
import styles from './SideNavLinks.module.scss'
import { SideNavToggleButton } from './SideNavToggleButton'

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
  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

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

  const isHubPage = location.pathname === '/hub'

  return isHubPage ? (
    <HubPageNavigation isLateralPanelOpen={isLateralPanelOpen} />
  ) : (
    <div
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-with-padding-top']]: !withSwitchVenueFeature,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      {withSwitchVenueFeature && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          to="/remboursements"
          iconPosition={IconPositionEnum.LEFT}
          icon={strokeRepaymentIcon}
          className={styles['back-to-partner-space-button']}
        >
          Espace Administration
        </ButtonLink>
      )}
      {selectedOfferer && (
        <div className={styles['nav-links-group']}>
          {withSwitchVenueFeature && selectedVenue && (
            <ButtonLink
              aria-label={`Changer de structure (actuellement sélectionnée : ${selectedVenue.name})`}
              className={styles['nav-links-switch-venue-button']}
              icon={fullLeftIcon}
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
          <SideNavLink to="/accueil" icon={strokeHomeIcon}>
            Accueil
          </SideNavLink>
        </li>

        {/* INDIVIDUEL */}
        <li>
          <SideNavToggleButton
            icon={strokePhoneIcon}
            title="Individuel"
            isExpanded={navOpenSection.individual}
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
            ariaControls="individual-sublist"
            id="individual-sublist-button"
          />

          {navOpenSection.individual && (
            <ul
              id="individual-sublist"
              aria-labelledby="individual-sublist-button"
            >
              <li>
                <SideNavLink to="/offres" end>
                  Offres
                </SideNavLink>
              </li>
              <li>
                <SideNavLink to="/reservations" end>
                  Réservations
                </SideNavLink>
              </li>
              <li>
                <SideNavLink to="/guichet">Guichet</SideNavLink>
              </li>
              {selectedOfferer && selectedPartnerPageVenueId && (
                <li>
                  <SideNavLink
                    to={`/structures/${selectedOfferer.id}/lieux/${selectedPartnerPageVenueId}/page-partenaire`}
                    end
                  >
                    Page sur l’application
                  </SideNavLink>
                </li>
              )}
            </ul>
          )}
        </li>

        {/* COLLECTIF */}
        <li>
          <SideNavToggleButton
            icon={strokeTeacherIcon}
            title="Collectif"
            isExpanded={navOpenSection.collective}
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
            ariaControls="collective-sublist"
            id="collective-sublist-button"
          />

          {navOpenSection.collective && (
            <ul
              id="collective-sublist"
              aria-labelledby="collective-sublist-button"
            >
              <li>
                <SideNavLink to="/offres/vitrines">Offres vitrines</SideNavLink>
              </li>
              <li>
                <SideNavLink to="/offres/collectives">
                  Offres réservables
                </SideNavLink>
              </li>

              {selectedOfferer && venueId && (
                <li>
                  <SideNavLink
                    to={`/structures/${selectedOfferer.id}/lieux/${venueId}/collectif`}
                    end
                  >
                    Page dans ADAGE
                  </SideNavLink>
                </li>
              )}
            </ul>
          )}
        </li>
      </ul>

      {withSwitchVenueFeature ? (
        <ul>
          <div className={styles['nav-links-group']}>
            <div
              className={styles['nav-links-last-group-separator']}
              aria-hidden="true"
            >
              <div className={styles['separator-line']} />
            </div>
            <li>
              <UserReviewDialog
                dialogTrigger={
                  <Button
                    variant={ButtonVariant.TERNARY}
                    icon={fullSmsIcon}
                    className={classnames(
                      styles['nav-links-item'],
                      styles['nav-links-item-feedback']
                    )}
                  >
                    Donner mon avis
                  </Button>
                }
              />
            </li>
            <li>
              <HelpDropdownNavItem isMobileScreen={isMobileScreen ?? false} />
            </li>
          </div>
        </ul>
      ) : (
        <div className={styles['nav-links-group']}>
          <div
            className={styles['nav-links-last-group-separator']}
            aria-hidden="true"
          >
            <div className={styles['separator-line']} />
          </div>
          <div>
            <SideNavLink
              to="/remboursements"
              icon={isCaledonian ? strokeFrancIcon : strokeEuroIcon}
            >
              Gestion financière
            </SideNavLink>
          </div>
          <div>
            <SideNavLink to="/collaborateurs" icon={strokeCollaboratorIcon}>
              Collaborateurs
            </SideNavLink>
          </div>
        </div>
      )}
    </div>
  )
}
