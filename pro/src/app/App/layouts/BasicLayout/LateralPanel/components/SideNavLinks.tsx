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
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
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
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'

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
            openIndividual === navOpenSection.individual
              ? navOpenSection.individual
              : openIndividual,
          collective:
            openCollective === navOpenSection.collective
              ? navOpenSection.collective
              : openCollective,
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
      {withSwitchVenueFeature && (
        <div className={styles['back-to-admin']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            to="/remboursements"
            iconPosition={IconPositionEnum.LEFT}
            icon={strokeRepaymentIcon}
            label="Espace Administration"
          />
        </div>
      )}
      {selectedOfferer && (
        <div
          className={classnames({
            [styles['nav-links-group-switch-venue']]: withSwitchVenueFeature,
            [styles['nav-links-group']]: !withSwitchVenueFeature,
          })}
        >
          {withSwitchVenueFeature && selectedVenue && (
            <div className={styles['nav-links-switch-venue-button']}>
              <Button
                as="a"
                aria-label={`Changer de structure (actuellement sélectionnée : ${selectedVenue.publicName})`}
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                icon={fullLeftIcon}
                to="/hub"
                label={
                  selectedVenue.publicName?.length > 20
                    ? `${selectedVenue.publicName.substring(0, 19)}...`
                    : selectedVenue.publicName
                }
                fullWidth
                fullHeight
              />
            </div>
          )}

          <div className={styles['nav-links-create-offer-wrapper']}>
            <DropdownButton
              name="Créer une offre"
              options={[
                {
                  element: (
                    <Button
                      as="a"
                      variant={ButtonVariant.TERTIARY}
                      color={ButtonColor.NEUTRAL}
                      to={getIndividualOfferUrl({
                        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                        mode: OFFER_WIZARD_MODE.CREATION,
                        isOnboarding: false,
                      })}
                      icon={strokePhoneIcon}
                      label="Pour le grand public"
                    />
                  ),
                  id: 'individual',
                },
                {
                  element: (
                    <Button
                      as="a"
                      variant={ButtonVariant.TERTIARY}
                      color={ButtonColor.NEUTRAL}
                      to="/offre/creation"
                      icon={strokeBagIcon}
                      label="Pour les groupes scolaires"
                    />
                  ),
                  id: 'collective',
                },
              ]}
              triggerProps={{
                fullWidth: true,
              }}
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
        <div className={styles['nav-links-group']}>
          <div
            className={styles['nav-links-last-group-separator']}
            aria-hidden="true"
          >
            <div className={styles['separator-line']} />
          </div>
          <ul>
            <li>
              <UserReviewDialog
                dialogTrigger={
                  <Button
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    icon={fullSmsIcon}
                    className={styles['nav-links-item']}
                    label="Donner mon avis"
                  />
                }
              />
            </li>
            <li>
              <HelpDropdownNavItem isMobileScreen={isMobileScreen ?? false} />
            </li>
          </ul>
        </div>
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
