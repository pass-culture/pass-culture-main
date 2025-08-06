import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import {
  type AggregatedRevenueModel,
  type GetOffererResponseModel,
  type GetOffererVenueResponseModel,
  type StatisticsModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import { statisticsFactory } from '@/commons/utils/factories/statisticsFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Income } from './Income'
import { isCollectiveAndIndividualRevenue, isCollectiveRevenue } from './utils'

const MOCK_DATA: {
  selectedOffererId: number
  offerer: GetOffererResponseModel & {
    managedVenues: Array<GetOffererVenueResponseModel>
  }
} & StatisticsModel = {
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
  ...statisticsFactory({
    emptyYear: '1994',
    individualRevenueOnlyYear: '1995',
    collectiveRevenueOnlyYear: '1996',
    collectiveAndIndividualRevenueYear: '1997',
    lastYear: '1997',
  }),
}

const LABELS = {
  error: /Erreur dans le chargement des données./,
  venuesSelector: /Partenaire/,
  venuesSelectorError: /Vous devez sélectionner au moins un partenaire/,
  incomeResultsLabel: /Chiffre d’affaires total/,
  forecastIncomeResultLabel: /Chiffre d’affaires total prévisionnel/,
  emptyScreen: /Vous n’avez aucune réservation/,
  mandatoryHelper: /\* sont obligatoires/,
}

const renderIncome = () => {
  renderWithProviders(<Income />, {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory({
        currentOfferer: { id: MOCK_DATA.selectedOffererId },
      }),
    },
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getStatistics: vi.fn(),
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
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByTestId('venues-spinner')).toBeInTheDocument()
      )
      expect(api.getOfferer).toHaveBeenNthCalledWith(
        1,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should display an error message if venues couldnt be fetched', async () => {
      vi.spyOn(api, 'getOfferer').mockRejectedValue(new Error('error'))
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.error)).toBeInTheDocument()
      )
      expect(api.getOfferer).toHaveBeenNthCalledWith(
        1,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should display an empty screen if no venues were found', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...MOCK_DATA.offerer,
        managedVenues: [],
      })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
      expect(api.getOfferer).toHaveBeenNthCalledWith(
        1,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should attempt to fetch income data with all venues and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() =>
        expect(screen.getByTestId('income-spinner')).toBeInTheDocument()
      )
      expect(api.getStatistics).toHaveBeenNthCalledWith(
        1,
        MOCK_DATA.offerer.managedVenues.map((venue) => venue.id)
      )
    })

    it('should display an error message if income couldnt be fetched', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockRejectedValue(new Error('error'))
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.error)).toBeInTheDocument()
      )
    })

    it('should display an empty screen if no income data was found', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({ incomeByYear: {} })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
    })

    it('should not display a venue selector, nor the mandatory input helper if there is only one venue', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...MOCK_DATA.offerer,
        managedVenues: [MOCK_DATA.offerer.managedVenues[0]],
      })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      // This is a check to avoid a false positive by testing existence
      // of element to prove conjoined non-existence of another.
      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBeGreaterThan(0)
      })

      expect(
        screen.queryByRole('button', {
          name: LABELS.venuesSelector,
        })
      ).not.toBeInTheDocument()

      expect(screen.queryByText(LABELS.mandatoryHelper)).not.toBeInTheDocument()
    })

    it('should display a set of year filters with the last year selected by default', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      const years = [...Object.keys(MOCK_DATA.incomeByYear)]
      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBe(years.length)
      })

      // Years are sorted in descending order, so the last/most recent year
      // is the first item of the list of filters.
      const mostRecentYear = years.sort((a, b) => parseInt(b) - parseInt(a))[0]
      expect(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${mostRecentYear}`,
        })
      ).toHaveAttribute('aria-current', 'true')
    })

    it('should auto-focus the last year filter if there is only one venue', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...MOCK_DATA.offerer,
        managedVenues: [MOCK_DATA.offerer.managedVenues[0]],
      })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBeGreaterThan(0)
      })

      const years = [...Object.keys(MOCK_DATA.incomeByYear)]
      // Years are sorted in descending order, so the last/most recent year
      // is the first item of the list of filters.
      const mostRecentYear = years.sort((a, b) => parseInt(b) - parseInt(a))[0]
      expect(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${mostRecentYear}`,
        })
      ).toHaveFocus()
    })

    it('should display the income results', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(
          screen.getAllByText(LABELS.incomeResultsLabel).length
        ).toBeGreaterThan(0)
      )
    })
  })

  describe('when the user changes venue selection', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should display an error if no venues are selected and avoid fetching income data', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => {
        expect(
          screen.getByRole('button', {
            name: LABELS.venuesSelector,
          })
        ).toBeInTheDocument()
      })

      const deleteVenueButtons = screen.getAllByRole('button', {
        name: /Supprimer/,
      })

      for (const button of deleteVenueButtons) {
        await userEvent.click(button)
      }

      await waitFor(
        () =>
          expect(
            screen.getByText(LABELS.venuesSelectorError)
          ).toBeInTheDocument(),
        {
          timeout: 3000,
        }
      )

      // It should not attempt to fetch income data if no venues are selected.
      expect(api.getStatistics).toHaveBeenCalledTimes(1)
    })

    it('should attempt to fetch income data with the selected venues and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => {
        expect(
          screen.getByRole('button', {
            name: LABELS.venuesSelector,
          })
        ).toBeInTheDocument()
      })

      const deleteVenueButtons = screen.getAllByRole('button', {
        name: /Supprimer/,
      })
      const unselectedVenue = deleteVenueButtons[0]
      await userEvent.click(unselectedVenue)

      await waitFor(() =>
        expect(screen.getByTestId('income-spinner')).toBeInTheDocument()
      )
      const expectedLeftVenueIds = MOCK_DATA.offerer.managedVenues
        .filter((v) => v.name !== unselectedVenue.textContent)
        .map((v) => v.id)
      expect(api.getStatistics).toHaveBeenNthCalledWith(2, expectedLeftVenueIds)
    })
  })

  describe('when the user changes year selection', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should display the income results for the selected year', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()
      const toLocalEur = (number: number): string =>
        number.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))
      const yearsWithData = Object.keys(MOCK_DATA.incomeByYear).filter(
        (year) => Object.keys(MOCK_DATA.incomeByYear[year]).length > 0
      )

      for (const y of yearsWithData) {
        await userEvent.click(
          screen.getByRole('button', {
            name: `Afficher les revenus de l'année ${y}`,
          })
        )

        const income = MOCK_DATA.incomeByYear[y]
        const incomeTypes = Object.keys(
          income
        ) as (keyof AggregatedRevenueModel)[]
        for (const t of incomeTypes) {
          const incomeResults = income[t]
          if (incomeResults) {
            if (isCollectiveAndIndividualRevenue(incomeResults)) {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.total), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
              expect(
                screen.getByText(toLocalEur(incomeResults.individual), {
                  collapseWhitespace: false,
                })
              ).toBeInTheDocument()
              expect(
                screen.getByText(toLocalEur(incomeResults.collective), {
                  collapseWhitespace: false,
                })
              ).toBeInTheDocument()
            } else if (isCollectiveRevenue(incomeResults)) {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.collective), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
            } else {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.individual), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
            }
          }
        }
      }
    })

    it('should display en empty screen if no data is available for the selected year', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))

      const emptyYear = Object.keys(MOCK_DATA.incomeByYear).find(
        (year) =>
          MOCK_DATA.incomeByYear[year].revenue === null &&
          MOCK_DATA.incomeByYear[year].expectedRevenue === null
      )
      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${emptyYear}`,
        })
      )

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
    })

    it('should display previsionnal income only for current year', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(MOCK_DATA.offerer)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))

      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année 1997`,
        })
      )

      expect(
        screen.getByText(LABELS.forecastIncomeResultLabel)
      ).toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année 1996`,
        })
      )

      expect(
        screen.queryByText(LABELS.forecastIncomeResultLabel)
      ).not.toBeInTheDocument()
    })
  })
})
