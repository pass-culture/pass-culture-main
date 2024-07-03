import cn from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import { Footer } from 'components/Footer/Footer'
import { Header } from 'components/Header/Header'
import { NewNavReview } from 'components/NewNavReview/NewNavReview'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import { useWithoutFrame } from 'hooks/useWithoutFrame'
import fullInfoIcon from 'icons/full-info.svg'
import { selectCurrentUser } from 'store/user/selectors'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { LateralPanel } from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

interface LayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const Layout = ({ children, layout = 'basic' }: LayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const shouldDisplayNewNavReview =
    Boolean(currentUser?.navState?.eligibilityDate) &&
    layout !== 'funnel' &&
    layout !== 'without-nav'

  const isWithoutFrame = useWithoutFrame()

  return (
    <>
      <div
        className={styles['layout']}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && lateralPanelOpen) {
            setLateralPanelOpen(false)
          }
        }}
      >
        <SkipLinks />
        {currentUser?.isImpersonated && (
          <aside className={styles['connect-as']}>
            <SvgIcon
              src={fullInfoIcon}
              alt="Information"
              width="20"
              className={styles['connect-as-icon']}
            />
            <div className={styles['connect-as-text']}>
              Vous êtes connecté en tant que :&nbsp;
              <strong>
                {currentUser.firstName} {currentUser.lastName}
              </strong>
            </div>
          </aside>
        )}
        {(layout === 'basic' || layout === 'sticky-actions') && (
          <Header
            lateralPanelOpen={lateralPanelOpen}
            setLateralPanelOpen={setLateralPanelOpen}
            focusCloseButton={() => {
              setTimeout(() => {
                closeButtonRef.current?.focus()
              })
            }}
            ref={openButtonRef}
          />
        )}
        <div
          className={cn(styles['page-layout'], {
            [styles['page-layout-funnel']]: layout === 'funnel',
          })}
        >
          {(layout === 'basic' || layout === 'sticky-actions') && (
            <LateralPanel
              lateralPanelOpen={lateralPanelOpen}
              setLateralPanelOpen={setLateralPanelOpen}
              openButtonRef={openButtonRef}
              closeButtonRef={closeButtonRef}
              navPanel={navPanel}
            />
          )}
          <div className={styles['content-wrapper']}>
            {shouldDisplayNewNavReview && <NewNavReview />}
            <div
              className={cn(styles['content-container'], {
                [styles['content-container-funnel']]: layout === 'funnel',
                [styles['content-container-without-frame']]: isWithoutFrame,
              })}
            >
              <main id="content">
                {layout === 'funnel' || layout === 'without-nav' ? (
                  children
                ) : (
                  <div
                    className={cn(styles.content, {
                      [styles['content-without-frame']]: isWithoutFrame,
                    })}
                  >
                    {children}
                  </div>
                )}
              </main>
              {layout !== 'funnel' && <Footer layout={layout} />}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
