import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { setColorThemePreference } from '@/commons/store/colorTheme/reducer'
import { selectColorThemePreference } from '@/commons/store/colorTheme/selectors'
import {
  applyColorTheme,
  getStoredColorThemePreference,
  PREFERS_DARK_COLOR_SCHEME_QUERY,
  resolveColorTheme,
} from '@/commons/utils/colorTheme'

export const useColorTheme = () => {
  const dispatch = useAppDispatch()
  const isDarkModeEnabled = useActiveFeature('WIP_ENABLE_PRO_DARK_MODE')
  const preference = useAppSelector(selectColorThemePreference)
  const prefersDarkColorScheme = Boolean(
    useMediaQuery(PREFERS_DARK_COLOR_SCHEME_QUERY)
  )
  const { pathname } = useLocation()
  // The Adage iframe is embedded in a third-party platform: it keeps the light theme.
  const isInAdageIframe = pathname.startsWith('/adage-iframe')

  useEffect(() => {
    dispatch(setColorThemePreference(getStoredColorThemePreference()))
  }, [dispatch])

  useEffect(() => {
    applyColorTheme(
      isDarkModeEnabled && !isInAdageIframe
        ? resolveColorTheme(preference, prefersDarkColorScheme)
        : 'light'
    )
  }, [isDarkModeEnabled, isInAdageIframe, preference, prefersDarkColorScheme])
}
