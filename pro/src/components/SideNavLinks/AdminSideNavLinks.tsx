import classnames from 'classnames'
import { useId, useState } from 'react'
import { NavLink, useLocation } from 'react-router'

import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  const location = useLocation()
  const dataId = useId()
  const dataSublistId = useId()

  const isIndividuelActive = location.pathname.startsWith(
    '/administration/individuel'
  )
  const isCollectifActive = location.pathname.startsWith(
    '/administration/collectif'
  )

  return (
    <>
      <div className={styles['nav-links-header']}>Espace Administration</div>
      <nav
        className={classnames({
          [styles['nav-links']]: true,
          [styles['nav-links-open']]: isLateralPanelOpen,
        })}
      >
        <ul className={styles['nav-links-group']}>
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
                src={strokeRepaymentIcon}
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
                    to="#"
                    end
                    className={() =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isIndividuelActive,
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
                    to="#"
                    end
                    className={() =>
                      classnames(styles['nav-links-item'], {
                        [styles['nav-links-item-active']]: isCollectifActive,
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
              to="/accueil"
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
      </nav>
    </>
  )
}
