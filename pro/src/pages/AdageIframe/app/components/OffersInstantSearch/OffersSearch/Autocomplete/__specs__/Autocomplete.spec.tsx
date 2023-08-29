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

const renderAutocomplete = ({ initialQuery }: { initialQuery: string }) => {
  return renderWithProviders(
    <Autocomplete
      initialQuery={initialQuery}
      placeholder={'Rechercher : nom de l’offre, partenaire culturel'}
    />
  )
}

describe('Autocomplete', () => {
  it('should renders the Autocomplete component with placeholder and search button', () => {
    renderAutocomplete({ initialQuery: '' })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    const searchButton = screen.getByText('Rechercher')

    expect(inputElement).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()
  })

  it('should call refine function when the form is submitted', async () => {
    renderAutocomplete({ initialQuery: '' })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    const searchButton = screen.getByText('Rechercher')

    await userEvent.type(inputElement, 'test query')

    userEvent.click(searchButton)

    await waitFor(() => expect(refineMock).toHaveBeenCalledWith('test query'))
  })

  it('should set an initial search value on init', async () => {
    renderAutocomplete({ initialQuery: 'test query 2' })

    const searchButton = screen.getByText('Rechercher')

    await userEvent.click(searchButton)

    const inputElement = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )

    expect(inputElement).toHaveValue('test query 2')
    expect(refineMock).toHaveBeenCalledWith('test query 2')
  })
})
