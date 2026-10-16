import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { ColorThemeToggle } from './ColorThemeToggle'

const renderColorThemeToggle = (
  options?: RenderWithProvidersOptions,
  onKeyDown = vi.fn()
) => renderWithProviders(<ColorThemeToggle onKeyDown={onKeyDown} />, options)

describe('ColorThemeToggle', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderColorThemeToggle()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render a named group with one toggle button per theme', () => {
    renderColorThemeToggle()

    const group = screen.getByRole('group', { name: 'Thème' })

    expect(group).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Thème clair' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Thème sombre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Thème du système' })
    ).toBeInTheDocument()
  })

  it('should select the system theme by default', () => {
    renderColorThemeToggle()

    expect(
      screen.getByRole('button', { name: 'Thème du système' })
    ).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'Thème clair' })).toHaveAttribute(
      'aria-pressed',
      'false'
    )
    expect(
      screen.getByRole('button', { name: 'Thème sombre' })
    ).toHaveAttribute('aria-pressed', 'false')
  })

  it('should select the current preference', () => {
    renderColorThemeToggle({
      storeOverrides: { colorTheme: { preference: 'light' } },
    })

    expect(screen.getByRole('button', { name: 'Thème clair' })).toHaveAttribute(
      'aria-pressed',
      'true'
    )
  })

  it('should select and store the chosen theme', async () => {
    renderColorThemeToggle()

    await userEvent.click(screen.getByRole('button', { name: 'Thème sombre' }))

    expect(
      screen.getByRole('button', { name: 'Thème sombre' })
    ).toHaveAttribute('aria-pressed', 'true')
    expect(
      screen.getByRole('button', { name: 'Thème du système' })
    ).toHaveAttribute('aria-pressed', 'false')
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.COLOR_THEME)).toBe('dark')
  })

  it('should forward key events to the parent', async () => {
    const onKeyDown = vi.fn()
    renderColorThemeToggle(undefined, onKeyDown)

    await userEvent.tab()
    expect(screen.getByRole('button', { name: 'Thème clair' })).toHaveFocus()

    await userEvent.keyboard('{Escape}')

    expect(onKeyDown).toHaveBeenCalledWith(
      expect.objectContaining({ key: 'Escape' })
    )
  })
})
