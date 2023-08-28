import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Autocomplete } from '../Autocomplete'

const refineMock = vi.fn()

const renderAutocomplete = ({
  placeholder,
  refine,
}: {
  placeholder: string
  refine: SearchBoxProvided['refine']
}) => {
  return renderWithProviders(
    <Autocomplete placeholder={placeholder} refine={refine} />
  )
}

describe('Autocomplete', () => {
  it('should renders the Autocomplete component with placeholder and search button', () => {
    renderAutocomplete({ placeholder: 'Search', refine: refineMock })

    const inputElement = screen.getByPlaceholderText('Search')
    const searchButton = screen.getByText('Rechercher')

    expect(inputElement).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()
  })

  it('should call refine function when the form is submitted', async () => {
    renderAutocomplete({ placeholder: 'Search', refine: refineMock })

    const inputElement = screen.getByPlaceholderText('Search')
    const searchButton = screen.getByText('Rechercher')

    await userEvent.type(inputElement, 'test query')

    userEvent.click(searchButton)

    await waitFor(() => expect(refineMock).toHaveBeenCalledWith('test query'))
  })
})
