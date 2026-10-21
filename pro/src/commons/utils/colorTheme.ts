import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export type ColorTheme = 'light' | 'dark'
export type ColorThemePreference = ColorTheme | 'system'

export const PREFERS_DARK_COLOR_SCHEME_QUERY = '(prefers-color-scheme: dark)'

const COLOR_THEME_PREFERENCES: ReadonlySet<ColorThemePreference> = new Set([
  'light',
  'dark',
  'system',
])

const isColorThemePreference = (
  value: string | null
): value is ColorThemePreference =>
  COLOR_THEME_PREFERENCES.has(value as ColorThemePreference)

export const getStoredColorThemePreference = (): ColorThemePreference => {
  const storedPreference = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.COLOR_THEME
  )

  return isColorThemePreference(storedPreference) ? storedPreference : 'system'
}

export const storeColorThemePreference = (
  preference: ColorThemePreference
): void => {
  localStorageManager.setItem(LOCAL_STORAGE_KEY.COLOR_THEME, preference)
}

export const resolveColorTheme = (
  preference: ColorThemePreference,
  prefersDarkColorScheme: boolean
): ColorTheme => {
  if (preference === 'system') {
    return prefersDarkColorScheme ? 'dark' : 'light'
  }

  return preference
}

/**
 * The design system tokens are scoped by the `data-theme` attribute of the root element.
 */
export const applyColorTheme = (colorTheme: ColorTheme): void => {
  document.documentElement.dataset.theme = colorTheme
}
