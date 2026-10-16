import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import type { ColorThemePreference } from '@/commons/utils/colorTheme'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useColorTheme } from '../useColorTheme'

vi.mock('@/commons/hooks/useMediaQuery', () => ({
  useMediaQuery: vi.fn(),
}))

const ColorThemeApplier = (): null => {
  useColorTheme()
  return null
}

const renderColorThemeApplier = ({
  isFeatureActive = true,
  preference,
  prefersDarkColorScheme = false,
  path = '/accueil',
}: {
  isFeatureActive?: boolean
  preference: ColorThemePreference
  prefersDarkColorScheme?: boolean
  path?: string
}) => {
  vi.mocked(useMediaQuery).mockReturnValue(prefersDarkColorScheme)
  localStorage.setItem(LOCAL_STORAGE_KEY.COLOR_THEME, preference)

  renderWithProviders(<ColorThemeApplier />, {
    features: isFeatureActive ? ['WIP_ENABLE_PRO_DARK_MODE'] : [],
    initialRouterEntries: [path],
    routes: [{ path, element: <ColorThemeApplier /> }],
  })
}

describe('useColorTheme', () => {
  afterEach(() => {
    localStorage.clear()
    document.documentElement.dataset.theme = 'light'
  })

  it('should keep the light theme when the feature is disabled', () => {
    renderColorThemeApplier({ isFeatureActive: false, preference: 'dark' })

    expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  })

  it.each([
    ['light', 'light'],
    ['dark', 'dark'],
  ] as const)(
    'should apply the %s theme when it is the stored preference',
    (preference, expectedTheme) => {
      document.documentElement.dataset.theme =
        expectedTheme === 'light' ? 'dark' : 'light'

      renderColorThemeApplier({ preference })

      expect(document.documentElement).toHaveAttribute(
        'data-theme',
        expectedTheme
      )
    }
  )

  it.each([
    [true, 'dark'],
    [false, 'light'],
  ])(
    'should follow the system theme (prefers dark: %s) when the preference is system',
    (prefersDarkColorScheme, expectedTheme) => {
      renderColorThemeApplier({ preference: 'system', prefersDarkColorScheme })

      expect(document.documentElement).toHaveAttribute(
        'data-theme',
        expectedTheme
      )
    }
  )

  it('should keep the light theme in the Adage iframe', () => {
    renderColorThemeApplier({
      preference: 'dark',
      path: '/adage-iframe/recherche',
    })

    expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  })
})
