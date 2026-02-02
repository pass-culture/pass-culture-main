import classnames from 'classnames'
import { useId, useState } from 'react'
import { NavLink } from 'react-router'

import { UserReviewDialog } from '@/app/App/layouts/components/Header/components/UserReviewDialog/UserReviewDialog'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import fullDownIcon from '@/icons/full-down.svg'
import fullSmsIcon from '@/icons/full-sms.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import strokeReportIcon from '@/icons/stroke-report.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { HelpDropdownNavItem } from './HelpDropdownNavItem'
import styles from './SideNavLinks.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface AdminSideNavLinksProps {
  isLateralPanelOpen: boolean
}

type OpenSection = {
  data: boolean
}

export const AdminSideNavLinks = ({
  isLateralPanelOpen,
}: AdminSideNavLinksProps) => {
  const [openSection, setOpenSection] = useState<OpenSection>({ data: true })
  const dataId = useId()
  const dataSublistId = useId()

  // Used because `<DropdownMenu.Content />` `side` prop comes from `@radix-ui` and can't be handled via CSS unless by creating an intermediary UI component.
  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

  return (
    <nav
      className={classnames({
        [styles['nav-links']]: true,
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
      <ul className={styles['nav-links-group']}>
        <li>
          <NavLink
            to="/remboursements"
            className={({ isActive }) =>
              classnames(styles['nav-links-item'], {
                [styles['nav-links-item-active']]: isActive,
              })
            }
          >
            <SvgIcon
              src={strokeRepaymentIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles.icon}
            />
            <span className={styles['nav-links-item-title']}>
              Gestion financière
            </span>
          </NavLink>
        </li>
        <li>
          <button
            type="button"
            onClick={() =>
              setOpenSection((prev) => ({ ...prev, data: !prev.data }))
            }
            className={classnames(
              styles['nav-links-item'],
              styles['nav-section-button']
            )}
            aria-expanded={openSection.data}
            aria-controls={dataSublistId}
            id={dataId}
          >
            <SvgIcon
              src={strokeReportIcon}
              alt=""
              width={NAV_ITEM_ICON_SIZE}
              className={styles.icon}
            />
            <span className={styles['nav-section-title']}>
              Données d’activité
            </span>
            <SvgIcon
              src={openSection.data ? fullUpIcon : fullDownIcon}
              alt=""
              width="18"
              className={styles['nav-section-icon']}
            />
          </button>
          {openSection.data && (
            <ul id={dataSublistId} aria-labelledby={dataId}>
              <li>
                <NavLink
                  to="/admin/individuel"
                  end
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Individuel
                  </span>
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/admin/collectif"
                  end
                  className={({ isActive }) =>
                    classnames(styles['nav-links-item'], {
                      [styles['nav-links-item-active']]: isActive,
                    })
                  }
                >
                  <span className={styles['nav-links-item-without-icon']}>
                    Collectif
                  </span>
                </NavLink>
              </li>
            </ul>
          )}
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
              className={styles.icon}
            />
            <span className={styles['nav-links-item-title']}>
              Collaborateurs
            </span>
          </NavLink>
        </li>
      </ul>
      <div
        className={styles['nav-links-last-group-separator']}
        aria-hidden="true"
      >
        <div className={styles['separator-line']} />
      </div>
      <ul className={styles['nav-links-footer']}>
        <li>
          <UserReviewDialog
            dialogTrigger={
              <Button
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                icon={fullSmsIcon}
                className={classnames(styles['nav-links-item'])}
                label="Donner mon avis"
              />
            }
          />
        </li>
        <li>
          <HelpDropdownNavItem isMobileScreen={isMobileScreen ?? false} />
        </li>
      </ul>
    </nav>
  )
}
