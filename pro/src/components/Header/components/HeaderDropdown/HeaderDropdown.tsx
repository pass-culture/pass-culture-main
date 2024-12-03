import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFERER_NAMES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { updateSelectedOffererId } from 'commons/store/user/reducer'
import {
  selectCurrentOffererId,
  selectCurrentUser,
} from 'commons/store/user/selectors'
import { getSavedOffererId } from 'commons/utils/getSavedOffererId'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import { sortByLabel } from 'commons/utils/strings'
import fulBackIcon from 'icons/full-back.svg'
import fullCloseIcon from 'icons/full-close.svg'
import fullLogoutIcon from 'icons/full-logout.svg'
import fullMoreIcon from 'icons/full-more.svg'
import fullProfilIcon from 'icons/full-profil.svg'
import fullSwitchIcon from 'icons/full-switch.svg'
import fulValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { HelpDropdownMenu } from '../HeaderHelpDropdown/HelpDropdownMenu'

import styles from './HeaderDropdown.module.scss'

export const HeaderDropdown = () => {
  const { logEvent } = useAnalytics()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const currentUser = useSelector(selectCurrentUser)
  const currentOffererId = useSelector(selectCurrentOffererId)
  const dispatch = useDispatch()
  const [windowWidth, setWindowWidth] = useState(window.innerWidth)
  const [subOpen, setSubOpen] = useState(false)
  const sideOffset =
    windowWidth >= 673
      ? 20
      : -(windowWidth - (16 + (windowWidth >= 380 ? 17 : 0)))

  const offererNamesQuery = useSWR([GET_OFFERER_NAMES_QUERY_KEY], () =>
    api.listOfferersNames()
  )
  const offererNames = offererNamesQuery.data?.offerersNames

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

  const handleChangeOfferer = (newOffererId: string) => {
    if (Number(newOffererId) !== selectedOffererId) {
      dispatch(updateSelectedOffererId(Number(newOffererId)))
      if (localStorageAvailable()) {
        localStorage.setItem(SAVED_OFFERER_ID_KEY, newOffererId)
      }
    }
  }

  if (offererOptions.length && !currentOffererId) {
    setTimeout(() => {
      handleChangeOfferer(selectedOffererId.toString())
    })
  }

  if (offererOptions.length && !selectedOffererName) {
    setTimeout(() => {
      handleChangeOfferer(offererOptions[0]?.value)
    })
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

  return (
    <DropdownMenu.Root onOpenChange={() => setSubOpen(false)}>
      <DropdownMenu.Trigger asChild>
        <button
          className={styles['dropdown-button']}
          title={selectedOffererName?.name || 'Profil'}
          data-testid="offerer-select"
        >
          <SvgIcon src={fullProfilIcon} alt="" width="18" />
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
            {offererOptions.length > 1 && (
              <>
                {!isOfferAddressEnabled && (
                  <DropdownMenu.Label
                    data-testid="offerer-header-label"
                    className={styles['menu-title']}
                  >
                    Structure
                  </DropdownMenu.Label>
                )}
                <div className={styles['menu-email']}>
                  {selectedOffererName?.name}
                </div>

                <DropdownMenu.Sub open={subOpen}>
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
                      Changer{!isOfferAddressEnabled && ' de structure'}
                    </Button>
                  </DropdownMenu.SubTrigger>
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
                        <div className={styles['sub-popin-header-text']}>
                          Structure
                        </div>
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
                            Ajouter
                            {!isOfferAddressEnabled &&
                              ' une nouvelle structure'}
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
