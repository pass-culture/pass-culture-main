/** biome-ignore-all lint/correctness/useUniqueElementIds: SideNavLinks is used once per page. There cannot be id duplications. */

import classnames from 'classnames'
import { useState } from 'react'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import { Dropdown } from '@/design-system/Dropdown/Dropdown'
import fullDownIcon from '@/icons/full-down.svg'
import fullLeftIcon from '@/icons/full-left.svg'
import fullParametersIcon from '@/icons/full-parameters.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeHomeIcon from '@/icons/stroke-home.svg'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'

import { type NavItem, SideNavLinks } from '../SideNavLinks/SideNavLinks'
import styles from './LateralMenu.module.scss'

interface SideNavLinksProps {
  isLateralPanelOpen: boolean
}

const generateNavItems = (): NavItem[] => {
  const individualChildren: NavItem[] = [
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
    {
      key: 'page',
      type: 'link',
      group: 'main' as const,
      title: 'Page sur l’application',
      to: `/partenaire/page-partenaire`,
    },
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
    {
      key: 'adage_page',
      type: 'link',
      group: 'main' as const,
      title: 'Page dans ADAGE',
      to: `/partenaire/page-collective`,
    },
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
      children: individualChildren,
    },
    {
      type: 'section',
      group: 'main',
      title: 'Collectif',
      icon: strokeTeacherIcon,
      key: 'collective',
      children: collectifChildren,
    },
    {
      type: 'link',
      group: 'main',
      title: 'Paramètres',
      to: '/parametres',
      icon: fullParametersIcon,
      key: 'settings',
    },
  ]

  return navItems
}

export const LateralMenu = ({ isLateralPanelOpen }: SideNavLinksProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )
  if (!selectedPartnerVenue) {
    return null
  }

  const navItems = generateNavItems()

  return (
    <div
      className={classnames(styles['nav-links'], {
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      <div className={styles['back-to-admin']}>
        <Button
          as="router-link"
          variant={ButtonVariant.SECONDARY}
          to="/remboursements"
          iconPosition={IconPositionEnum.LEFT}
          icon={strokeRepaymentIcon}
          label="Espace administration"
          fullWidth
        />
      </div>

      <div className={styles['nav-links-group-switch-venue']}>
        <div className={styles['nav-links-switch-venue-button']}>
          <Button
            as="router-link"
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

        <div className={styles['nav-section-create-button-wrapper']}>
          {!withVenueHelpers(selectedPartnerVenue).isClosed && (
            <Dropdown
              label="Créer une offre"
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
              items={[
                [
                  {
                    text: 'Pour le grand public',
                    icon: strokePhoneIcon,
                    link: {
                      to: getIndividualOfferUrl({
                        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                        mode: OFFER_WIZARD_MODE.CREATION,
                        isOnboarding: false,
                      }),
                    },
                  },
                  {
                    text: 'Pour les groupes scolaires',
                    icon: strokeBagIcon,
                    link: {
                      to: '/offre/creation',
                    },
                  },
                ],
              ]}
            />
          )}
          {withVenueHelpers(selectedPartnerVenue).isClosed && (
            <Button disabled fullWidth label="Créer une offre" />
          )}
        </div>
      </div>

      <SideNavLinks navItems={navItems} />
    </div>
  )
}
