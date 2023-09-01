import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Autocomplete } from '../Autocomplete'

const refineMock = vi.fn()

vi.mock('react-instantsearch-dom', async () => {
  return {
    ...((await vi.importActual('react-instantsearch-dom')) ?? {}),
    Configure: vi.fn(() => <div />),
    connectSearchBox: vi
      .fn()
      .mockImplementation(Component => (props: SearchBoxProvided) => (
        <Component {...props} refine={refineMock} />
      )),
  }
})

const renderAutocomplete = ({
  initialQuery,
  featuresOverride = null,
}: {
  initialQuery: string
  featuresOverride?: { nameKey: string; isActive: boolean }[] | null
}) => {
  const storeOverrides = {
    features: {
      list: featuresOverride,
      initialized: true,
    },
  }

  return renderWithProviders(
    <div>
      <a href="#">First element</a>
      <Autocomplete
        initialQuery={initialQuery}
        placeholder={
          'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
        }
      />
      <a href="#">Second element</a>
    </div>,
    { storeOverrides }
  )
}

describe('Autocomplete', () => {
  it('should renders the Autocomplete component with placeholder and search button', () => {
    renderAutocomplete({ initialQuery: '' })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
    const searchButton = screen.getByText('Rechercher')

    expect(inputElement).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()
  })

  it('should close autocomplete panel when escape key pressed  ', async () => {
    const featuresOverride = [
      {
        nameKey: 'WIP_ENABLE_SEARCH_HISTORY_ADAGE',
        isActive: true,
      },
    ]
    renderAutocomplete({ initialQuery: '', featuresOverride })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    const searchButton = screen.getByText('Rechercher')
    const dialogElement = screen.getByTestId('dialog')

    await userEvent.type(inputElement, 'test')

    await userEvent.click(searchButton)
    await userEvent.click(inputElement)

    await userEvent.keyboard('{Escape}')

    expect(dialogElement).not.toHaveAttribute('open')
  })

  it('should close autocomplete panel when focus outside form ', async () => {
    const featuresOverride = [
      {
        nameKey: 'WIP_ENABLE_SEARCH_HISTORY_ADAGE',
        isActive: true,
      },
    ]
    renderAutocomplete({ initialQuery: '', featuresOverride })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    const searchButton = screen.getByText('Rechercher')
    const dialogElement = screen.getByTestId('dialog')
    const footerButton = screen.getByText('Comment fonctionne la recherche ?')

    await userEvent.type(inputElement, 'test')

    await userEvent.click(searchButton)
    await userEvent.click(inputElement)

    await userEvent.tab()
    await userEvent.tab()
    await userEvent.tab()

    expect(footerButton).toHaveFocus()

    await userEvent.tab()
    expect(dialogElement).not.toHaveAttribute('open')
  })

  it('should call refine function when the form is submitted', async () => {
    renderAutocomplete({ initialQuery: '' })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
    const searchButton = screen.getByText('Rechercher')

    await userEvent.type(inputElement, 'test query')

    userEvent.click(searchButton)

    await waitFor(() => expect(refineMock).toHaveBeenCalledWith('test query'))
  })

  it('should set an initial search value on init', async () => {
    renderAutocomplete({
      initialQuery: 'test query 2',
    })

    const searchButton = screen.getByText('Rechercher')

    await userEvent.click(searchButton)

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    expect(inputElement).toHaveValue('test query 2')
    expect(refineMock).toHaveBeenCalledWith('test query 2')
  })

  it('should clear recent search when clear button is clicked', async () => {
    const featuresOverride = [
      {
        nameKey: 'WIP_ENABLE_SEARCH_HISTORY_ADAGE',
        isActive: true,
      },
    ]

    renderAutocomplete({
      initialQuery: '',
      featuresOverride,
    })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
    const searchButton = screen.getByText('Rechercher')

    const panelElement = screen.getByTestId('dialog-panel')

    await userEvent.type(inputElement, 'test1')

    await userEvent.click(searchButton)

    await userEvent.click(inputElement)

    const clearButton = screen.getByText('Effacer')

    await userEvent.click(clearButton)

    await userEvent.click(inputElement)

    expect(panelElement).toHaveClass('dialog-panel-hide')
  })
})
