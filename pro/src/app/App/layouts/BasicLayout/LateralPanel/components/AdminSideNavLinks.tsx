import classnames from 'classnames'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeReportIcon from '@/icons/stroke-report.svg'

import { LateralMenu } from './SideNavLinks'
import styles from './SideNavLinks.module.scss'

interface AdminSideNavLinksProps {
  isLateralPanelOpen: boolean
}

export const AdminSideNavLinks = ({
  isLateralPanelOpen,
}: AdminSideNavLinksProps) => {
  const navItems = [
    {
      group: 'main',
      type: 'link',
      icon: strokeRepaymentIcon,
      title: 'Gestion financière',
      to: '/remboursements',
    },
    {
      type: 'section',
      group: 'main',
      icon: strokeReportIcon,
      title: 'Données d’activité',
      children: [
        {
          type: 'link',
          group: 'main',
          title: 'Individuel',
          to: '/admin/individuel',
        },
        {
          type: 'link',
          group: 'main',
          title: 'Collectif',
          to: '/admin/collectif',
        },
      ],
    },
    {
      group: 'main',
      type: 'link',
      icon: strokeCollaboratorIcon,
      title: 'Collaborateurs',
      to: '/collaborateurs',
    },
  ]

  return (
    <nav
      className={classnames(styles['nav-links'], {
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      <div className={styles['back-to-partner-space-button']}>
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

      <LateralMenu navItems={navItems} withSwitchVenueFeature={true} />
    </nav>
  )
}
