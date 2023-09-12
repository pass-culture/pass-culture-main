import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Autocomplete } from '../Autocomplete'

interface getItems {
  objectID: string
  query: string
  popularity: number
  nb_words: number
}

const refineMock = vi.fn()
const mockVenueSuggestions = [
  {
    objectID: '1',
    query: '',
    popularity: 1,
    nb_words: 1,
    label: 'Mock Venue 1',
    venue: {
      name: 'Mock Venue 1',
      publicName: 'Mock Venue 1',
    },
    offerer: {
      name: 'Mock Offerer 1',
    },
  },
  {
    objectID: '2',
    query: '',
    popularity: 1,
    nb_words: 1,
    label: 'Mock Venue 2',
    venue: {
      name: 'Mock Venue 2',
      publicName: 'Mock Venue 2',
    },
    offerer: {
      name: 'Mock Offerer 2',
    },
  },
]

const mockKeywordSuggestions = [
  {
    objectID: 'mock keyword 1',
    query: 'mock keyword 1',
    popularity: 1,
    nb_words: 1,
    'offer.subcategoryId': ['FESTIVAL_SPECTACLE'],
    querySuggestionName: {
      exact_nb_hits: 10,
    },
  },
  {
    objectID: 'mock keyword 2',
    query: 'mock keyword 2',
    popularity: 2,
    nb_words: 1,
    'offer.subcategoryId': ['RENCONTRE'],
    querySuggestionName: {
      exact_nb_hits: 5,
    },
  },
]

let mockGetItems = vi.fn((): Array<getItems> => mockVenueSuggestions)
let mockSourceId = 'VenueSuggestionsSource'

vi.mock('@algolia/autocomplete-plugin-query-suggestions', () => {
  return {
    ...vi.importActual('@algolia/autocomplete-plugin-query-suggestions'),
    createQuerySuggestionsPlugin: vi.fn(() => {
      return {
        name: 'querySuggestionName',
        getSources: () => [
          {
            sourceId: mockSourceId,
            getItems: mockGetItems,
          },
        ],
      }
    }),
  }
})

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
    <AdageUserContext.Provider value={{ adageUser: defaultAdageUser }}>
      <div>
        <a href="#">First element</a>
        <Autocomplete
          initialQuery={initialQuery}
          placeholder={
            'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
          }
          setCurrentSearch={vi.fn()}
        />
        <a href="#">Second element</a>
      </div>
    </AdageUserContext.Provider>
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
    renderAutocomplete({ initialQuery: '' })

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
    renderAutocomplete({ initialQuery: '' })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    const searchButton = screen.getByText('Rechercher')
    const dialogElement = screen.getByTestId('dialog')
    // TODO : uncomment when the link is added
    // const footerButton = screen.getByText('Comment fonctionne la recherche ?')

    await userEvent.click(searchButton)
    await userEvent.click(inputElement)

    await userEvent.tab()
    await userEvent.tab()
    await userEvent.tab()

    // TODO : uncomment when the link is added
    // expect(footerButton).toHaveFocus()

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
    renderAutocomplete({
      initialQuery: '',
    })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
    const searchButton = screen.getByText('Rechercher')

    await userEvent.click(searchButton)

    await userEvent.click(inputElement)

    const clearButton = screen.getByText('Effacer')

    await userEvent.click(clearButton)

    await userEvent.click(inputElement)
  })

  it('should display venue suggestion when user start to type', async () => {
    renderAutocomplete({
      initialQuery: '',
    })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    await userEvent.type(inputElement, 'M')

    const venueSuggestion = screen.getAllByText('Mock Venue 1')[0]

    expect(venueSuggestion).toBeInTheDocument()
  })

  it('should display word suggestion when user start to type', async () => {
    mockGetItems = vi.fn(() => mockKeywordSuggestions)
    mockSourceId = 'KeywordQuerySuggestionsSource'

    renderAutocomplete({
      initialQuery: '',
    })

    const inputElement = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )

    await userEvent.type(inputElement, 'mock')

    const keywordSuggestion = screen.getAllByText(/mock keyword 1/)[0]

    expect(keywordSuggestion).toBeInTheDocument()
  })
})
