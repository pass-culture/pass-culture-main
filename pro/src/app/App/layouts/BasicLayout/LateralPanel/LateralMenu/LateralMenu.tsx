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
import { selectSelectedPartnerPageId } from '@/commons/store/nav/selector'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
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

const generateNavItems = (
  selectedOfferer?: GetOffererResponseModel | null,
  selectedPartnerPageVenueId?: string | number,
  venueId?: string | number,
  isVolunteeringActive?: boolean
): NavItem[] => {
  const hasSeenVolunteeringSection =
    localStorageManager.getItem(
      LOCAL_STORAGE_KEY.HAS_SEEN_VOLUNTEERING_SECTION
    ) === 'true'

  const individuelChildren: NavItem[] = [
    {
      key: 'offers',
      type: 'link',
      group: 'main',
      title: 'Offres',
      to: '/offres',
      end: true,
    },
    {
      key: 'reservation',
      type: 'link',
      group: 'main',
      title: 'Réservations',
      to: '/reservations',
      end: true,
    },
    {
      key: 'ticket_office',
      type: 'link',
      group: 'main',
      title: 'Guichet',
      to: '/guichet',
    },
    ...(selectedOfferer && selectedPartnerPageVenueId
      ? [
          {
            key: 'page',
            type: 'link',
            group: 'main' as const,
            title: 'Page sur l’application',
            to: `/structures/${selectedOfferer.id}/lieux/${selectedPartnerPageVenueId}/page-partenaire`,
            end: true,
            showNotification:
              isVolunteeringActive && !hasSeenVolunteeringSection,
          },
        ]
      : []),
  ]

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
    ...(selectedOfferer && venueId
      ? [
          {
            key: 'adage_page',
            type: 'link',
            group: 'main' as const,
            title: 'Page dans ADAGE',
            to: `/structures/${selectedOfferer.id}/lieux/${venueId}/collectif`,
            end: true,
          },
        ]
      : []),
  ]

  const navItems: NavItem[] = [
    {
      key: 'home',
      type: 'link',
      group: 'main',
      title: 'Accueil',
      to: '/accueil',
      icon: strokeHomeIcon,
    },
    {
      type: 'section',
      group: 'main',
      title: 'Individuel',
      icon: strokePhoneIcon,
      key: 'individual',
      children: individuelChildren,
    },
    {
      type: 'section',
      group: 'main',
      title: 'Collectif',
      icon: strokeTeacherIcon,
      key: 'collective',
      children: collectifChildren,
    },
  ]

  return navItems
}

export const LateralMenu = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const isVolunteeringActive = useActiveFeature('WIP_VOLUNTEERING')

  const selectedOfferer = useAppSelector(
    (state) => state.offerer.currentOfferer
  )
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.isPermanent) ?? []
  const hasPartnerPageVenues =
    selectedOfferer?.managedVenues?.filter((v) => v.hasPartnerPage) ?? []
  const venueId = withSwitchVenueFeature
    ? selectedPartnerVenue?.id
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
    isVolunteeringActive
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
          {withSwitchVenueFeature && selectedPartnerVenue && (
            <div className={styles['nav-links-switch-venue-button']}>
              <Button
                as="a"
                aria-label={`Changer de structure (actuellement sélectionnée : ${selectedPartnerVenue.publicName})`}
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                icon={fullLeftIcon}
                to="/hub"
                label={selectedPartnerVenue.publicName}
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
