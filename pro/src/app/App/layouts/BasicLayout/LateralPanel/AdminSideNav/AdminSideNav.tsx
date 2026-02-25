import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeReportIcon from '@/icons/stroke-report.svg'

import { type NavItem, SideNavLinks } from '../SideNavLinks/SideNavLinks'
import styles from './AdminSideNav.module.scss'

export const AdminSideNavLinks = () => {
  const navItems: NavItem[] = [
    {
      key: 'financial_management',
      group: 'main',
      type: 'link',
      icon: strokeRepaymentIcon,
      title: 'Gestion financière',
      to: '/remboursements',
    },
    {
      key: 'activity_data',
      type: 'section',
      group: 'main',
      icon: strokeReportIcon,
      title: 'Données d’activité',
      children: [
        {
          key: 'individual_admin',
          type: 'link',
          group: 'main',
          title: 'Individuel',
          to: '/administration/donnees-activite/individuel',
        },
        {
          key: 'collective_admin',
          type: 'link',
          group: 'main',
          title: 'Collectif',
          to: '/administration/donnees-activite/collectif',
        },
      ],
    },
    {
      key: 'collaborators_admin',
      group: 'main',
      type: 'link',
      icon: strokeCollaboratorIcon,
      title: 'Collaborateurs',
      to: '/collaborateurs',
    },
  ]

  return (
    <nav className={styles['nav-links']}>
      <div className={styles['back-to-admin']}>
        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          to="/accueil"
          iconPosition={IconPositionEnum.LEFT}
          icon={fullBackIcon}
          label="Revenir à l’Espace Partenaire"
          fullWidth
        />
      </div>

      <div className={styles['nav-links-header']}>Espace Administration</div>

      <SideNavLinks navItems={navItems} withSwitchVenueFeature={true} />
    </nav>
  )
}
