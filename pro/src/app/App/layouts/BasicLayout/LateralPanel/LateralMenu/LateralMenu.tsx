/** biome-ignore-all lint/correctness/useUniqueElementIds: SideNavLinks is used once per page. There cannot be id duplications. */

import classnames from 'classnames'
import { useState } from 'react'
import { Link } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { selectSelectedPartnerPageId } from '@/commons/store/nav/selector'
import { getSavedPartnerPageVenueId } from '@/commons/utils/savedPartnerPageVenueId'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullLeftIcon from '@/icons/full-left.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import strokeHomeIcon from '@/icons/stroke-home.svg'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

import { type NavItem, SideNavLinks } from '../SideNavLinks/SideNavLinks'
import styles from './LateralMenu.module.scss'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

function generateNavItems(
  selectedOfferer?: GetOffererResponseModel | null,
  selectedPartnerPageVenueId?: string | number,
  venueId?: string | number,
  isCaledonian?: boolean
): NavItem[] {
  const navItems: NavItem[] = []

  // ===== MAIN LINKS =====
  navItems.push({
    key: 'home',
    type: 'link',
    group: 'main',
    title: 'Accueil',
    to: '/accueil',
    icon: strokeHomeIcon,
  })

  // ===== Individuel Section =====
  const individuelChildren: NavItem[] = [
    {
      key: 'offers',
      type: 'link',
      group: 'main',
      title: 'Offres',
      to: '/offres',
    },
    {
      key: 'reservation',
      type: 'link',
      group: 'main',
      title: 'Réservations',
      to: '/reservations',
    },
    {
      key: 'ticket_office',
      type: 'link',
      group: 'main',
      title: 'Guichet',
      to: '/guichet',
    },
  ]

  if (selectedOfferer && selectedPartnerPageVenueId) {
    individuelChildren.push({
      key: 'page',
      type: 'link',
      group: 'main',
      title: 'Page sur l’application',
      to: `/structures/${selectedOfferer.id}/lieux/${selectedPartnerPageVenueId}/page-partenaire`,
    })
  }

  navItems.push({
    type: 'section',
    group: 'main',
    title: 'Individuel',
    icon: strokePhoneIcon,
    key: 'individual',
    children: individuelChildren,
  })

  // ===== Collectif Section =====
  const collectifChildren: NavItem[] = [
    {
      key: 'showcase_offers',
      type: 'link',
      group: 'main',
      title: 'Offres vitrines',
      to: '/offres/vitrines',
    },
    {
      key: 'bookable_offers',
      type: 'link',
      group: 'main',
      title: 'Offres réservables',
      to: '/offres/collectives',
    },
  ]

  if (selectedOfferer && venueId) {
    collectifChildren.push({
      key: 'adage_page',
      type: 'link',
      group: 'main',
      title: 'Page dans ADAGE',
      to: `/structures/${selectedOfferer.id}/lieux/${venueId}/collectif`,
    })
  }

  navItems.push({
    type: 'section',
    group: 'main',
    title: 'Collectif',
    icon: strokeTeacherIcon,
    key: 'collective',
    children: collectifChildren,
  })

  // ===== FOOTER =====

  navItems.push(
    {
      key: 'refunds',
      group: 'footer',
      type: 'link',
      title: 'Gestion financière',
      to: '/remboursements',
      icon: isCaledonian ? strokeFrancIcon : strokeEuroIcon,
    },
    {
      key: 'collaborators',
      group: 'footer',
      type: 'link',
      title: 'Collaborateurs',
      to: '/collaborateurs',
      icon: strokeCollaboratorIcon,
    }
  )

  return navItems
}

export const LateralMenu = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const isCaledonian = useIsCaledonian()

  const selectedOfferer = useAppSelector(
    (state) => state.offerer.currentOfferer
  )
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.isPermanent) ?? []
  const hasPartnerPageVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.hasPartnerPage) ?? []
  const venueId = withSwitchVenueFeature
    ? selectedVenue?.id
    : permanentVenues[0]?.id

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

  const [isOpen, setIsOpen] = useState(false)

  const navItems = generateNavItems(
    selectedOfferer,
    selectedPartnerPageVenueId,
    venueId,
    isCaledonian
  )

  return (
    <div
      className={classnames(styles['nav-links'], {
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
            fullWidth
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
                  selectedVenue.publicName?.length > 19
                    ? `${selectedVenue.publicName.substring(0, 18)}...`
                    : selectedVenue.publicName
                }
                fullWidth
                fullHeight
              />
            </div>
          )}

          <div className={styles['nav-section-create-button-wrapper']}>
            <Dropdown
              title="Créer une offre"
              open={isOpen}
              onOpenChange={setIsOpen}
              align="start"
              trigger={
                <Button
                  label="Créer une offre"
                  variant={ButtonVariant.PRIMARY}
                  icon={isOpen ? fullUpIcon : fullDownIcon}
                  iconPosition={IconPositionEnum.RIGHT}
                  fullWidth
                />
              }
            >
              <DropdownItem icon={strokePhoneIcon}>
                <Link
                  to={getIndividualOfferUrl({
                    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                    mode: OFFER_WIZARD_MODE.CREATION,
                    isOnboarding: false,
                  })}
                >
                  Pour le grand public
                </Link>
              </DropdownItem>
              <DropdownItem icon={strokeBagIcon}>
                <Link to="/offre/creation">Pour les groupes scolaires</Link>
              </DropdownItem>
            </Dropdown>
          </div>
        </div>
      )}

      <SideNavLinks
        navItems={navItems}
        withSwitchVenueFeature={withSwitchVenueFeature}
      />
    </div>
  )
}
