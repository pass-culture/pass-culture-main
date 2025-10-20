import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setSelectedVenueById } from '@/commons/store/user/dispatchers/setSelectedVenueById'
import fullDownIcon from '@/icons/full-down.svg'
import fulValidateIcon from '@/icons/full-validate.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'
import styles from './HeaderVenuesDropdown.module.scss'

export const HeaderVenuesDropdown = () => {
  const dispatch = useAppDispatch()
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)
  const venues = useAppSelector((state) => state.user.venues)

  if (!venues?.length || !selectedVenue) {
    return null
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant={ButtonVariant.QUATERNARY}
          icon={fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Structure
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={dropdownStyles['pop-in']}
          align="end"
          sideOffset={16}
        >
          <div className={cn(dropdownStyles['menu'], styles['menu'])}>
            <DropdownMenu.RadioGroup
              onValueChange={(nextSelectedVenueId) =>
                dispatch(setSelectedVenueById(nextSelectedVenueId))
              }
              className={dropdownStyles['menu-group']}
              value={selectedVenue.id.toString()}
            >
              {venues.map((venue) => (
                <DropdownMenu.RadioItem
                  asChild
                  className={dropdownStyles['menu-item']}
                  key={venue.id}
                  title={venue.name}
                  value={venue.id.toString()}
                >
                  <div>
                    <span className={dropdownStyles['menu-item-name']}>
                      {venue.name}
                    </span>

                    {venue.id === selectedVenue.id && (
                      <SvgIcon
                        src={fulValidateIcon}
                        alt=""
                        width="16"
                        className={dropdownStyles['menu-item-check']}
                      />
                    )}
                  </div>
                </DropdownMenu.RadioItem>
              ))}
            </DropdownMenu.RadioGroup>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
