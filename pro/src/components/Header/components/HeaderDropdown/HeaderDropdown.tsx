import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import {
  selectCurrentOffererId,
  selectOffererNames,
} from 'commons/store/offerer/selectors'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { getSavedOffererId } from 'commons/utils/getSavedOffererId'
import { hardRefresh } from 'commons/utils/hardRefresh'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { sortByLabel } from 'commons/utils/strings'
import { resetAllStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import fulBackIcon from 'icons/full-back.svg'
import fullCloseIcon from 'icons/full-close.svg'
import fullLogoutIcon from 'icons/full-logout.svg'
import fullMoreIcon from 'icons/full-more.svg'
import fullProfilIcon from 'icons/full-profil.svg'
import fullSmsIcon from 'icons/full-sms.svg'
import fullSwitchIcon from 'icons/full-switch.svg'
import fulValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { HelpDropdownMenu } from '../HeaderHelpDropdown/HelpDropdownMenu'
import { UserReviewDialog } from '../UserReviewDialog/UserReviewDialog'

import styles from './HeaderDropdown.module.scss'

export const HeaderDropdown = () => {
  const { logEvent } = useAnalytics()
  const isProFeedbackEnabled = useActiveFeature('ENABLE_PRO_FEEDBACK')

  const currentUser = useSelector(selectCurrentUser)
  const currentOffererId = useSelector(selectCurrentOffererId)
  const offererNames = useSelector(selectOffererNames)
  const [windowWidth, setWindowWidth] = useState(window.innerWidth)
  const [subOpen, setSubOpen] = useState(false)
  const sideOffset =
    windowWidth >= 673
      ? 20
      : -(windowWidth - (16 + (windowWidth >= 380 ? 17 : 0)))

  const offererOptions = sortByLabel(
    offererNames?.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    })) ?? []
  )
  const { pathname } = useLocation()
  const IN_STRUCTURE_CREATION_FUNNEL = pathname.startsWith(
    '/parcours-inscription'
  )
  const hideProfile =
    IN_STRUCTURE_CREATION_FUNNEL && offererOptions.length === 0

  const selectedOffererId =
    currentOffererId ??
    getSavedOffererId(offererOptions) ??
    (offererOptions.length > 0 ? offererOptions[0]?.value : '')

  const selectedOffererName = offererNames?.find(
    (offererOption) => offererOption.id === Number(selectedOffererId)
  )
  const handleChangeOfferer = (newOffererId: string): void => {
    // Reset offers stored search filters before changing offerer
    resetAllStoredFilterConfig()

    // Updates offerer id in storage
    if (storageAvailable('localStorage')) {
      localStorage.setItem(SAVED_OFFERER_ID_KEY, newOffererId)
    }

    // Hard refresh to homepage after offerer change
    hardRefresh('/accueil')
  }

  useEffect(() => {
    if (offererOptions.length && !currentOffererId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      handleChangeOfferer(selectedOffererId.toString())
    }

    if (offererOptions.length && !selectedOffererName) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      handleChangeOfferer(offererOptions[0]?.value)
    }
  })

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <DropdownMenu.Root onOpenChange={() => setSubOpen(false)}>
      <DropdownMenu.Trigger asChild>
        <button
          className={styles['dropdown-button']}
          data-testid="offerer-select"
          type="button"
        >
          <SvgIcon src={fullProfilIcon} alt="Profil" width="18" />
          {offererOptions.length > 1 && (
            <span className={styles['dropdown-button-name']}>
              {selectedOffererName?.name}
            </span>
          )}
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={styles['pop-in']}
          align="end"
          sideOffset={7}
        >
          <div
            className={styles['menu']}
            data-testid="header-dropdown-menu-div"
          >
            <DropdownMenu.Item className={styles['close-item']}>
              <button className={styles['close-button']}>
                <SvgIcon
                  src={fullCloseIcon}
                  alt=""
                  width="24"
                  className={styles['close-button-icon']}
                />
              </button>
            </DropdownMenu.Item>
            {offererOptions.length >= 1 && (
              <>
                <div className={styles['menu-email']}>
                  {selectedOffererName?.name}
                </div>

                <DropdownMenu.Sub open={subOpen}>
                  {offererOptions.length > 1 ? (
                    <DropdownMenu.SubTrigger
                      asChild
                      onClick={() => setSubOpen(!subOpen)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === 'Space') {
                          setSubOpen(!subOpen)
                        }
                      }}
                    >
                      <Button
                        variant={ButtonVariant.TERNARY}
                        icon={fullSwitchIcon}
                        className={styles['menu-item']}
                      >
                        Changer
                      </Button>
                    </DropdownMenu.SubTrigger>
                  ) : (
                    <DropdownMenu.Item className={styles['menu-item']} asChild>
                      <ButtonLink
                        icon={fullMoreIcon}
                        className={styles['menu-item']}
                        to="/parcours-inscription/structure"
                      >
                        Ajouter une structure
                      </ButtonLink>
                    </DropdownMenu.Item>
                  )}
                  <DropdownMenu.Portal>
                    <DropdownMenu.SubContent
                      loop
                      sideOffset={sideOffset}
                      avoidCollisions={true}
                      className={styles['sub-popin']}
                    >
                      <div className={styles['sub-popin-header']}>
                        <Button
                          icon={fulBackIcon}
                          variant={ButtonVariant.TERNARY}
                          onClick={() => setSubOpen(false)}
                        >
                          Retour
                        </Button>
                      </div>
                      <div
                        className={styles['sub-menu']}
                        data-testid="offerers-selection-menu"
                      >
                        <DropdownMenu.RadioGroup
                          onValueChange={handleChangeOfferer}
                          className={styles['menu-group']}
                          value={selectedOffererName?.id.toString()}
                        >
                          {offererOptions.map((offererOption) => (
                            <DropdownMenu.RadioItem
                              key={offererOption.value}
                              asChild
                              value={offererOption.value}
                              className={cn(
                                styles['menu-item'],
                                styles['menu-item-sub']
                              )}
                            >
                              <div>
                                <span className={styles['menu-item-name']}>
                                  {offererOption.label}
                                </span>
                                {selectedOffererName?.id ===
                                  Number(offererOption.value) && (
                                  <SvgIcon
                                    src={fulValidateIcon}
                                    alt=""
                                    width="16"
                                    className={styles['menu-item-check']}
                                  />
                                )}
                              </div>
                            </DropdownMenu.RadioItem>
                          ))}
                        </DropdownMenu.RadioGroup>
                        <DropdownMenu.Separator
                          className={styles['separator']}
                        />
                        <DropdownMenu.Item asChild>
                          <ButtonLink
                            icon={fullMoreIcon}
                            className={styles['menu-item']}
                            to="/parcours-inscription/structure"
                          >
                            Ajouter une structure
                          </ButtonLink>
                        </DropdownMenu.Item>
                      </div>
                    </DropdownMenu.SubContent>
                  </DropdownMenu.Portal>
                </DropdownMenu.Sub>
                <DropdownMenu.Separator className={styles['separator']} />
              </>
            )}

            <DropdownMenu.Label className={styles['menu-title']}>
              Profil
            </DropdownMenu.Label>
            <div className={styles['menu-email']}>{currentUser?.email}</div>
            {!hideProfile && (
              <DropdownMenu.Item className={styles['menu-item']} asChild>
                <ButtonLink icon={fullProfilIcon} to="/profil">
                  Voir mon profil
                </ButtonLink>
              </DropdownMenu.Item>
            )}
            <DropdownMenu.Separator
              className={cn(styles['separator'], styles['tablet-only'])}
            />
            <DropdownMenu.Label
              className={cn(styles['menu-title'], styles['tablet-only'])}
            >
              Centre d’aide
            </DropdownMenu.Label>
            <div className={styles['tablet-only']}>
              <HelpDropdownMenu />
            </div>
            <DropdownMenu.Separator className={styles['separator']} />

            {isProFeedbackEnabled && (
              <>
                <div
                  className={cn(
                    styles['tablet-only'],
                    styles['menu-item-review-dialog']
                  )}
                >
                  <UserReviewDialog
                    dialogTrigger={
                      <DropdownMenu.Item
                        asChild
                        onSelect={(e) => e.preventDefault()} //  Necessary to prenent selecting the item from closing the DropdownMenu
                      >
                        <Button
                          variant={ButtonVariant.TERNARY}
                          icon={fullSmsIcon}
                        >
                          Donner mon avis
                        </Button>
                      </DropdownMenu.Item>
                    }
                  />
                </div>
                <DropdownMenu.Separator
                  className={cn(styles['tablet-only'], styles['separator'])}
                />
              </>
            )}
            <DropdownMenu.Item className={styles['menu-item']} asChild>
              <ButtonLink
                icon={fullLogoutIcon}
                to={`${pathname}?logout`}
                onClick={() =>
                  logEvent(Events.CLICKED_LOGOUT, {
                    from: pathname,
                  })
                }
              >
                Se déconnecter
              </ButtonLink>
            </DropdownMenu.Item>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
