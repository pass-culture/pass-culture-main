import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { Income, MOCK_INCOME_BY_YEAR } from './Income'
import { IncomeResults, IncomeType } from './types'

const MOCK_DATA = {
  selectedOffererId: 100,
  offerer: {
    ...defaultGetOffererResponseModel,
    managedVenues: [
      {
        ...defaultGetOffererVenueResponseModel,
        id: 1,
        name: 'mk2 - Bibliothèque',
      },
      {
        ...defaultGetOffererVenueResponseModel,
        id: 2,
        name: 'mk2 - Odéon',
      },
      {
        ...defaultGetOffererVenueResponseModel,
        id: 3,
        name: 'mk2 - Nation',
      },
    ],
  },
}

const LABELS = {
  error: /Erreur dans le chargement des données./,
  venuesSelector: /Partenaire/,
  incomeResultsLabel: /Chiffre d’affaires total/,
  emptyScreen: /Vous n’avez aucune réservation/,
  mandatoryHelper: /\* sont obligatoires/,
}

const renderIncome = () => {
  renderWithProviders(<Income />, {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedOffererId: MOCK_DATA.selectedOffererId,
      },
    },
  })
}

vi.mock('apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
  },
}))

describe('Income', () => {
  describe('when the page first renders', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should attempt to fetch venues data and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      renderIncome()

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      expect(api.getOfferer).toHaveBeenCalledWith(MOCK_DATA.selectedOffererId)
    })

    it('should display an error message if venues couldnt be fetched', async () => {
      vi.spyOn(api, 'getOfferer').mockRejectedValue(new Error('error'))
      renderIncome()

      await waitFor(() => {
        expect(screen.getByText(LABELS.error)).toBeInTheDocument()
      })
    })

    it('should display an empty screen if no venues were found', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...MOCK_DATA.offerer,
        managedVenues: [],
      })
      renderIncome()

      await waitFor(() => {
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      })
    })

    // TODO : https://passculture.atlassian.net/browse/PC-32278
    it('should attempt to fetch income data with all venues and display a loading spinner meanwhile', () => {})
    it('should display an error message if income couldnt be fetched', () => {})
    it('should display an empty screen if no income data was found', () => {})

    it('should display a venue selector with all venues selected by default', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      renderIncome()

      await waitFor(() => {
        expect(
          screen.getByRole('combobox', {
            name: LABELS.venuesSelector,
          })
        ).toBeInTheDocument()

        MOCK_DATA.offerer.managedVenues.forEach((venue) => {
          expect(
            screen.getByRole('button', {
              name: `Supprimer ${venue.name}`,
            })
          ).toBeInTheDocument()
        })
      })
    })

    it('should not display a venue selector, nor the mandatory input helper if there is only one venue', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      renderIncome()

      await waitFor(() => {
        expect(
          screen.queryByRole('combobox', {
            name: LABELS.venuesSelector,
          })
        ).not.toBeInTheDocument()

        expect(
          screen.queryByText(LABELS.mandatoryHelper)
        ).not.toBeInTheDocument()
      })
    })

    it('should display a set of year filters with the last year selected by default', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      renderIncome()

      await waitFor(() => {
        const years = Object.keys(MOCK_INCOME_BY_YEAR)
        years.forEach((year) => {
          expect(
            screen.getByRole('button', {
              name: `Afficher les revenus de l'année ${year}`,
            })
          ).toBeInTheDocument()
        })
      })
    })

    it('should display the income results', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      renderIncome()

      await waitFor(() => {
        const resultTitles = screen.getAllByText(LABELS.incomeResultsLabel)
        expect(resultTitles.length).toBeGreaterThan(0)
      })
    })
  })

  describe('when the user changes venue selection', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    // TODO : https://passculture.atlassian.net/browse/PC-32278
    it('should display an error if no venues are selected', () => {})
    it('should attempt to fetch income data with the selected venues and display a loading spinner meanwhile', () => {})
  })

  describe('when the user changes year selection', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should display the income results for the selected year', async () => {
      renderIncome()
      const toFloatStr = (number: number): string =>
        number.toString().replace('.', ',') + '€'

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))
      const yearsWithData = Object.keys(MOCK_INCOME_BY_YEAR).filter(
        (year) =>
          Object.keys(MOCK_INCOME_BY_YEAR[year as unknown as number]).length > 0
      )

      for (const y of yearsWithData) {
        await userEvent.click(
          screen.getByRole('button', {
            name: `Afficher les revenus de l'année ${y}`,
          })
        )

        const income = MOCK_INCOME_BY_YEAR[y as unknown as number]
        const incomeTypes = Object.keys(income) as IncomeType[]
        for (const t of incomeTypes) {
          await waitFor(() => {
            const incomeResults = income[t] as IncomeResults
            const { total, individual, group } = incomeResults
            expect(screen.getByText(toFloatStr(total))).toBeInTheDocument()
            if (individual && group) {
              expect(
                screen.getAllByText(toFloatStr(individual)).length
              ).toBeGreaterThan(0)
              expect(
                screen.getAllByText(toFloatStr(group)).length
              ).toBeGreaterThan(0)
            }
          })
        }
      }
    })

    it('should display en empty screen if no data is available for the selected year', async () => {
      renderIncome()

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))
      const emptyYear = 2021
      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${emptyYear}`,
        })
      )
      await waitFor(() => {
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      })
    })
  })
})
