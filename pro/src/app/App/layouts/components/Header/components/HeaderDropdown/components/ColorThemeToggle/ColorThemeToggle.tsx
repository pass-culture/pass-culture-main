import type { KeyboardEvent } from 'react'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setColorThemePreference } from '@/commons/store/colorTheme/reducer'
import { selectColorThemePreference } from '@/commons/store/colorTheme/selectors'
import {
  type ColorThemePreference,
  storeColorThemePreference,
} from '@/commons/utils/colorTheme'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullDesktopIcon from '@/icons/full-desktop.svg'
import fullMoonIcon from '@/icons/full-moon.svg'
import fullSunIcon from '@/icons/full-sun.svg'

import styles from './ColorThemeToggle.module.scss'

const COLOR_THEME_OPTIONS: ReadonlyArray<{
  value: ColorThemePreference
  label: string
  icon: string
}> = [
  { value: 'light', label: 'Thème clair', icon: fullSunIcon },
  { value: 'dark', label: 'Thème sombre', icon: fullMoonIcon },
  { value: 'system', label: 'Thème du système', icon: fullDesktopIcon },
]

interface ColorThemeToggleProps {
  onKeyDown: (event: KeyboardEvent) => void
}

export const ColorThemeToggle = ({
  onKeyDown,
}: Readonly<ColorThemeToggleProps>) => {
  const dispatch = useAppDispatch()
  const preference = useAppSelector(selectColorThemePreference)

  const handleChange = (newPreference: ColorThemePreference) => {
    dispatch(setColorThemePreference(newPreference))
    storeColorThemePreference(newPreference)
  }

  return (
    <fieldset>
      <legend className={styles['color-theme-toggle-legend']}>Thème</legend>
      <div className={styles['color-theme-toggle-buttons']}>
        {COLOR_THEME_OPTIONS.map(({ value, label, icon }) => {
          const isSelected = preference === value

          return (
            <Button
              key={value}
              icon={icon}
              tooltip={label}
              aria-pressed={isSelected}
              variant={
                isSelected ? ButtonVariant.SECONDARY : ButtonVariant.TERTIARY
              }
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              onClick={() => handleChange(value)}
              onKeyDown={onKeyDown}
            />
          )
        })}
      </div>
    </fieldset>
  )
}
