import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectOffererNames } from '@/commons/store/offerer/selectors'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { setSelectedOffererById } from '@/commons/store/user/dispatchers/setSelectedOffererById'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fulBackIcon from '@/icons/full-back.svg'
import fullCloseIcon from '@/icons/full-close.svg'
import fullLogoutIcon from '@/icons/full-logout.svg'
import fullMoreIcon from '@/icons/full-more.svg'
import fullProfilIcon from '@/icons/full-profil.svg'
import fullSmsIcon from '@/icons/full-sms.svg'
import fullSwitchIcon from '@/icons/full-switch.svg'
import fulValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { HelpDropdownMenu } from '../HeaderHelpDropdown/HelpDropdownMenu'
import { UserReviewDialog } from '../UserReviewDialog/UserReviewDialog'
import styles from './HeaderDropdown.module.scss'
import { resetAllStoredFilterConfig } from './utils/resetAllStoredFilterConfig'

export const HeaderDropdown = () => {
  const { logEvent } = useAnalytics()
  const isProFeedbackEnabled = useActiveFeature('ENABLE_PRO_FEEDBACK')
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const currentUser = useAppSelector(selectCurrentUser)
  const offererNames = useAppSelector(selectOffererNames)
  const selectedOffererName = useAppSelector(
    (state) => state.offerer.currentOffererName
  )

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
    '/inscription/structure'
  )
  const hideProfile =
    IN_STRUCTURE_CREATION_FUNNEL && offererOptions.length === 0

  const handleChangeOfferer = async (nextSelectedOffererId: string) => {
    // Reset offers stored search filters before changing offerer
    resetAllStoredFilterConfig()

    const newAccess = await dispatch(
      setSelectedOffererById({
        nextSelectedOffererId: Number(nextSelectedOffererId),
      })
    ).unwrap()
    if (newAccess === 'full') {
      navigate('/accueil')
    }
  }

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  const logEventAndLogout = async () => {
    logEvent(Events.CLICKED_LOGOUT, {
      from: pathname,
    })

    await logout()
  }

  return (
    <DropdownMenu.Root onOpenChange={() => setSubOpen(false)}>
      <DropdownMenu.Trigger asChild>
        <button
          className={styles['dropdown-button']}
          data-testid="profile-button"
          type="button"
        >
          <SvgIcon src={fullProfilIcon} alt="Profil" width="18" />
          {!withSwitchVenueFeature &&
            selectedOffererName &&
            offererOptions.length > 1 && (
              <span className={styles['dropdown-button-name']}>
                {selectedOffererName.name}
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
              <button
                type="button"
                aria-label="fermer"
                className={styles['close-button']}
              >
                <SvgIcon
                  src={fullCloseIcon}
                  alt=""
                  width="24"
                  className={styles['close-button-icon']}
                />
              </button>
            </DropdownMenu.Item>
            {!withSwitchVenueFeature && offererOptions.length >= 1 && (
              <>
                {selectedOffererName && (
                  <div className={styles['menu-email']}>
                    {selectedOffererName.name}
                  </div>
                )}

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
                      <div className={styles['menu-item']}>
                        <Button
                          variant={ButtonVariant.TERTIARY}
                          color={ButtonColor.NEUTRAL}
                          icon={fullSwitchIcon}
                          label="Changer"
                        />
                      </div>
                    </DropdownMenu.SubTrigger>
                  ) : (
                    <DropdownMenu.Item className={styles['menu-item']}>
                      <Button
                        as="a"
                        variant={ButtonVariant.TERTIARY}
                        color={ButtonColor.NEUTRAL}
                        icon={fullMoreIcon}
                        to="/inscription/structure/recherche"
                        label="Ajouter une structure"
                      />
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
                          variant={ButtonVariant.TERTIARY}
                          color={ButtonColor.NEUTRAL}
                          onClick={() => setSubOpen(false)}
                          label="Retour"
                        />
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
                        <DropdownMenu.Item className={styles['menu-item']}>
                          <Button
                            as="a"
                            icon={fullMoreIcon}
                            variant={ButtonVariant.TERTIARY}
                            color={ButtonColor.NEUTRAL}
                            to="/inscription/structure/recherche"
                            label="Ajouter une structure"
                          />
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
              <DropdownMenu.Item className={styles['menu-item']}>
                <Button
                  as="a"
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullProfilIcon}
                  to="/profil"
                  label="Voir mon profil"
                />
              </DropdownMenu.Item>
            )}
            <DropdownMenu.Separator
              className={cn(styles['separator'], {
                [styles['tablet-only']]: !withSwitchVenueFeature,
              })}
            />
            {!withSwitchVenueFeature && (
              <DropdownMenu.Label
                className={cn(styles['menu-title'], styles['tablet-only'])}
              >
                Centre d’aide
              </DropdownMenu.Label>
            )}
            {!withSwitchVenueFeature && (
              <div className={styles['tablet-only']}>
                <HelpDropdownMenu />
              </div>
            )}
            {!withSwitchVenueFeature && (
              <DropdownMenu.Separator className={styles['separator']} />
            )}

            {!withSwitchVenueFeature && isProFeedbackEnabled && (
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
                        onSelect={(e) => e.preventDefault()} //  Necessary to prevent selecting the item from closing the DropdownMenu
                      >
                        <Button
                          variant={ButtonVariant.TERTIARY}
                          color={ButtonColor.NEUTRAL}
                          icon={fullSmsIcon}
                          label="Donner mon avis"
                        />
                      </DropdownMenu.Item>
                    }
                  />
                </div>
                <DropdownMenu.Separator
                  className={cn(styles['tablet-only'], styles['separator'])}
                />
              </>
            )}
            <DropdownMenu.Item className={styles['menu-item']}>
              <Button
                icon={fullLogoutIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                onClick={logEventAndLogout}
                label="Se déconnecter"
              />
            </DropdownMenu.Item>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
