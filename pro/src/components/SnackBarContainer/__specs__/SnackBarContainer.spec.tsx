import { act, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useMediaQuery from '@/commons/hooks/useMediaQuery'
import {
  type ISnackBarItem,
  snackBarAdapter,
} from '@/commons/store/snackBar/reducer'
import { listSelector } from '@/commons/store/snackBar/selectors'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import {
  ANIMATION_DURATION,
  SHORT_TEXT_DURATION,
  SnackBarVariant,
} from '@/design-system/SnackBar/SnackBar'

describe('SnackBarContainer', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })

    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const renderSnackBarContainer = (
    snackBars: Omit<ISnackBarItem, 'createdAt'>[],
    isStickyBarOpen = false
  ) =>
    renderWithProviders(<SnackBarContainer />, {
      storeOverrides: {
        snackBar: {
          list: snackBarAdapter.getInitialState(
            undefined,
            snackBars as ISnackBarItem[]
          ),
          isStickyBarOpen,
        },
      },
    })

  const variants = Object.values(SnackBarVariant)

  it.each(variants)('should display given %s text with icon', (variant) => {
    const snackBar = {
      description: 'Mon petit succès',
      variant: variant,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    renderSnackBarContainer([snackBar])

    const snackBarElement = screen.getByTestId(`global-snack-bar-${variant}-0`)

    expect(snackBarElement).toBeInTheDocument()
    expect(snackBarElement).toHaveClass('show')
    expect(snackBarElement).toHaveClass(variant)
  })

  it('should remove notification after fixed show and transition duration', () => {
    const snackBar = {
      description: 'Mon petit succès',
      variant: SnackBarVariant.SUCCESS,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    renderSnackBarContainer([snackBar])

    // Avancer le temps pour déclencher l'auto-fermeture
    act(() => {
      vi.advanceTimersByTime(SHORT_TEXT_DURATION)
    })

    expect(screen.getByTestId('global-snack-bar-success-0')).toHaveClass('hide')

    // Avancer le temps pour l'animation de fermeture
    act(() => {
      vi.advanceTimersByTime(ANIMATION_DURATION)
    })

    expect(
      screen.queryByTestId('global-snack-bar-success-0')
    ).not.toBeInTheDocument()
  })

  it('should apply sticky bar class when isStickyBarOpen is true', () => {
    const snackBar = {
      description: 'Test',
      variant: SnackBarVariant.SUCCESS,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    const { container } = renderSnackBarContainer([snackBar], true)

    expect(container.firstChild).toHaveClass('with-sticky-action-bar')
  })

  it('should not apply sticky bar class when isStickyBarOpen is false', () => {
    const snackBar = {
      description: 'Test',
      variant: SnackBarVariant.SUCCESS,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    const { container } = renderSnackBarContainer([snackBar], false)

    expect(container.firstChild).not.toHaveClass('with-sticky-action-bar')
  })

  it('should display multiple snackbars', () => {
    const snackBars = [
      { description: 'First', variant: SnackBarVariant.SUCCESS, id: '1' },
      { description: 'Second', variant: SnackBarVariant.ERROR, id: '2' },
    ] satisfies Omit<ISnackBarItem, 'createdAt'>[]

    renderSnackBarContainer(snackBars)

    expect(screen.getByTestId('global-snack-bar-success-0')).toBeInTheDocument()
    expect(screen.getByTestId('global-snack-bar-error-1')).toBeInTheDocument()
  })

  it('should remove snackbar from store when auto-closed', () => {
    const snackBar = {
      description: 'Test',
      variant: SnackBarVariant.SUCCESS,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    const { store } = renderSnackBarContainer([snackBar])

    expect(listSelector(store.getState())).toHaveLength(1)

    // Avancer le temps pour l'auto-fermeture + animation
    act(() => {
      vi.advanceTimersByTime(SHORT_TEXT_DURATION + ANIMATION_DURATION)
    })

    expect(listSelector(store.getState())).toHaveLength(0)
  })

  it('should remove snackbar from store when manually closed', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    const snackBar = {
      description: 'Test',
      variant: SnackBarVariant.SUCCESS,
      id: '123',
    } satisfies Omit<ISnackBarItem, 'createdAt'>

    const { store } = renderSnackBarContainer([snackBar])

    expect(listSelector(store.getState())).toHaveLength(1)

    const closeButton = screen.getByRole('button', {
      name: 'Fermer le message',
    })
    await user.click(closeButton)

    // Avancer le temps pour l'animation de fermeture
    act(() => {
      vi.advanceTimersByTime(ANIMATION_DURATION)
    })

    expect(listSelector(store.getState())).toHaveLength(0)
  })

  it('should sort snackbars in ascending order on small screen', () => {
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)

    const now = new Date()
    // Passer les snackbars dans un ordre différent pour tester le tri
    const snackBars = [
      {
        description: 'Third',
        variant: SnackBarVariant.SUCCESS,
        id: '3',
        createdAt: now.toISOString(), // Le plus récent
      },
      {
        description: 'First',
        variant: SnackBarVariant.SUCCESS,
        id: '1',
        createdAt: new Date(now.getTime() - 2000).toISOString(), // Le plus ancien
      },
      {
        description: 'Second',
        variant: SnackBarVariant.ERROR,
        id: '2',
        createdAt: new Date(now.getTime() - 1000).toISOString(), // Au milieu
      },
    ] satisfies ISnackBarItem[]

    renderWithProviders(<SnackBarContainer />, {
      storeOverrides: {
        snackBar: {
          list: snackBarAdapter.getInitialState(undefined, snackBars),
          isStickyBarOpen: false,
        },
      },
    })

    // Sur petit écran, les snackbars doivent être triés en ordre croissant
    // (le plus ancien en premier)
    expect(screen.getByTestId('global-snack-bar-success-0')).toHaveTextContent(
      'First'
    )
    expect(screen.getByTestId('global-snack-bar-error-1')).toHaveTextContent(
      'Second'
    )
    expect(screen.getByTestId('global-snack-bar-success-2')).toHaveTextContent(
      'Third'
    )
  })
})
