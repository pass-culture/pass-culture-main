import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { SuggestionType } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { defaultAdageUser } from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import * as storageAvailable from '@/commons/utils/storageAvailable'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import { AdageUserContext } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import type { SearchFormValues } from '../../../OffersInstantSearch'
import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../../utils'
import { Autocomplete } from '../Autocomplete'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logTrackingAutocompleteSuggestionClick: vi.fn(),
  },
}))

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
      id: '1',
      name: 'Mock Venue 1',
      publicName: 'Mock Venue 1',
      departmentCode: '75',
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
      id: '2',
      name: 'Mock Venue 2',
      publicName: 'Mock Venue 2',
      departmentCode: '75',
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
    formats: ['Atelier de pratique'],
    querySuggestionName: {
      exact_nb_hits: 10,
    },
  },
  {
    objectID: 'mock keyword 2',
    query: 'mock keyword 2',
    popularity: 2,
    nb_words: 1,
    formats: ['Concert'],
    querySuggestionName: {
      exact_nb_hits: 5,
    },
  },
  {
    objectID: 'mock keyword 3',
    query: 'mock keyword 3',
    popularity: 3,
    nb_words: 1,
    querySuggestionName: {
      exact_nb_hits: 5,
    },
    formats: [],
  },
]

let mockGetItems = vi.fn((): Array<getItems> => mockVenueSuggestions)
let mockSourceId = 'VenueSuggestionsSource'

vi.mock('@algolia/autocomplete-plugin-query-suggestions', () => {
  return {
    ...vi.importActual('@algolia/autocomplete-plugin-query-suggestions'),
    createQuerySuggestionsPlugin: vi.fn(
      (options?: { transformSource?: Function }) => {
        const baseSource = {
          sourceId: mockSourceId,
          getItems: mockGetItems,
        }

        const finalSource = options?.transformSource
          ? {
              ...options.transformSource({ source: baseSource }),
              getItems: mockGetItems,
            }
          : baseSource

        return {
          name: 'querySuggestionName',
          getSources: () => [finalSource],
        }
      }
    ),
  }
})

vi.mock('react-instantsearch', async () => {
  return {
    ...(await vi.importActual('react-instantsearch')),
    useSearchBox: () => ({ refine: refineMock }),
    useInstantSearch: () => ({ refresh: vi.fn() }),
  }
})

const renderAutocomplete = (
  initialQuery: string = '',
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(
    <>
      <AdageUserContext.Provider value={{ adageUser: defaultAdageUser }}>
        <div>
          <a href="#">First element</a>
          <Autocomplete initialQuery={initialQuery} handleSubmit={() => {}} />
          <a href="#">Second element</a>
        </div>
      </AdageUserContext.Provider>
      <SnackBarContainer />
    </>,
    options
  )
}

describe('Autocomplete', () => {
  it('should renders the Autocomplete component with placeholder and search button', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })

    expect(inputElement).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()
  })

  it('should close autocomplete panel when escape key pressed  ', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })
    const dialogElement = screen.getByTestId('dialog')

    await userEvent.type(inputElement, 'test')

    await userEvent.click(searchButton)
    await userEvent.click(inputElement)

    await userEvent.keyboard('{Escape}')

    expect(dialogElement).not.toHaveAttribute('open')
  })

  it('should close autocomplete panel when focus outside form ', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })
    const dialogElement = screen.getByTestId('dialog')

    await userEvent.click(searchButton)
    await userEvent.click(inputElement)

    await userEvent.tab()
    await userEvent.tab()
    await userEvent.tab()

    expect(dialogElement).not.toHaveAttribute('open')
  })

  it('should call refine function when the form is submitted', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.type(inputElement, 'test query')

    await userEvent.click(searchButton)

    await waitFor(() => expect(refineMock).toHaveBeenCalledWith('test query'))
  })

  it('should set an initial search value on init', async () => {
    renderAutocomplete('test query 2')

    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.click(searchButton)

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    expect(inputElement).toHaveValue('test query 2')
    expect(refineMock).toHaveBeenCalledWith('test query 2')
  })

  it('should clear recent search when clear button is clicked', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.click(searchButton)

    await userEvent.click(inputElement)

    const clearButton = screen.getByText('Effacer')

    await userEvent.click(clearButton)

    await userEvent.click(inputElement)
  })

  it('should disable saved history when cookies are disabled', async () => {
    renderAutocomplete()

    vi.spyOn(storageAvailable, 'storageAvailable').mockImplementation(
      () => false
    )

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
    const searchButton = await screen.findByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.type(inputElement, 'test query')

    await userEvent.click(searchButton)

    await userEvent.clear(inputElement)

    await userEvent.click(searchButton)

    await userEvent.click(inputElement)

    expect(screen.queryByText('Effacer')).not.toBeInTheDocument()
  })

  it('should display venue suggestion when user start to type', async () => {
    renderAutocomplete()

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    await userEvent.type(inputElement, 'M')

    const venueSuggestion = screen.getAllByText('Mock Venue 1')[0]

    expect(venueSuggestion).toBeInTheDocument()
  })

  it('should display word suggestion when user start to type', async () => {
    mockGetItems = vi.fn().mockImplementation(() => mockKeywordSuggestions)
    mockSourceId = 'KeywordQuerySuggestionsSource'

    renderAutocomplete('')

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    await userEvent.type(inputElement, 'mock')

    const keywordSuggestion = screen.getAllByText(/mock keyword 1/)[0]

    expect(keywordSuggestion).toBeInTheDocument()
  })

  it('should display format value for suggestion word ', async () => {
    mockGetItems = vi.fn().mockImplementation(() => mockKeywordSuggestions)
    mockSourceId = 'KeywordQuerySuggestionsSource'

    renderAutocomplete('mock keyword 1')

    const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })

    await userEvent.click(inputElement)

    expect(await screen.findByText('Atelier de pratique')).toBeInTheDocument()
  })

  describe('venue suggestions onSelect', () => {
    const renderAutocompleteWithForm = (
      initialQuery: string = '',
      handleSubmitMock: () => void = vi.fn(),
      initialFormValues: Partial<SearchFormValues> = {}
    ) => {
      const AutocompleteWithForm = () => {
        const form = useForm<SearchFormValues>({
          defaultValues: {
            ...ADAGE_FILTERS_DEFAULT_VALUES,
            ...initialFormValues,
          },
        })

        return (
          <FormProvider {...form}>
            <AdageUserContext.Provider value={{ adageUser: defaultAdageUser }}>
              <Autocomplete
                initialQuery={initialQuery}
                handleSubmit={handleSubmitMock}
              />
            </AdageUserContext.Provider>
          </FormProvider>
        )
      }

      return renderWithProviders(<AutocompleteWithForm />)
    }

    beforeEach(() => {
      mockGetItems = vi.fn().mockImplementation(() => mockVenueSuggestions)
      mockSourceId = 'VenueSuggestionsSource'
      vi.mocked(apiAdage.logTrackingAutocompleteSuggestionClick).mockClear()
    })

    it('should call handleSubmit and refine when venue suggestion is clicked', async () => {
      const handleSubmitMock = vi.fn()
      renderAutocompleteWithForm('', handleSubmitMock)

      const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
      await userEvent.type(inputElement, 'Mock')

      const venueSuggestions = await screen.findAllByText('Mock Venue 1')
      await userEvent.click(venueSuggestions[0])

      await waitFor(() => {
        expect(handleSubmitMock).toHaveBeenCalled()
      })
      expect(refineMock).toHaveBeenCalledWith('')
    })

    it('should log autocomplete suggestion click when venue is selected', async () => {
      renderAutocompleteWithForm('')

      const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
      await userEvent.type(inputElement, 'Mock')

      const venueSuggestions = await screen.findAllByText('Mock Venue 1')
      await userEvent.click(venueSuggestions[0])

      await waitFor(() => {
        expect(
          apiAdage.logTrackingAutocompleteSuggestionClick
        ).toHaveBeenCalledWith({
          iframeFrom: '/',
          suggestionType: SuggestionType.VENUE,
          suggestionValue: 'Mock Venue 1',
        })
      })
    })

    it('should add venue selection to history when localStorage is available', async () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      vi.spyOn(storageAvailable, 'storageAvailable').mockReturnValue(true)

      renderAutocompleteWithForm('')

      const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
      await userEvent.type(inputElement, 'Mock')

      const venueSuggestions = await screen.findAllByText('Mock Venue 1')
      await userEvent.click(venueSuggestions[0])

      await waitFor(() => {
        expect(setItemSpy).toHaveBeenCalledWith(
          'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH',
          expect.stringContaining('Mock Venue 1')
        )
      })

      setItemSpy.mockRestore()
    })

    it('should not add to history when localStorage is not available', async () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      vi.spyOn(storageAvailable, 'storageAvailable').mockReturnValue(false)

      renderAutocompleteWithForm('')

      const inputElement = screen.getByRole('searchbox', { name: 'Rechercher' })
      await userEvent.type(inputElement, 'Mock')

      const venueSuggestions = await screen.findAllByText('Mock Venue 1')
      await userEvent.click(venueSuggestions[0])

      await waitFor(() => {
        expect(
          apiAdage.logTrackingAutocompleteSuggestionClick
        ).toHaveBeenCalled()
      })

      expect(setItemSpy).not.toHaveBeenCalledWith(
        'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH',
        expect.stringContaining('Mock Venue 1')
      )

      setItemSpy.mockRestore()
    })
  })
})
