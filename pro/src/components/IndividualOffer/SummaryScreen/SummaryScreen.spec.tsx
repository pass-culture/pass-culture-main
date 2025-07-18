import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { add, format, set, sub } from 'date-fns'
import { Route, Routes } from 'react-router'
import { vi } from 'vitest'

import { api } from 'apiClient/api'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CATEGORY_STATUS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'

import { SummaryScreen } from './SummaryScreen'

vi.mock('apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    patchPublishOffer: vi.fn(),
  },
}))
vi.mock('commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
vi.mock('use-debounce', async () => ({
  ...(await vi.importActual('use-debounce')),
  useDebouncedCallback: vi.fn((fn) => fn),
}))

const LABELS = {
  publicationModeNowRadio: /Publier maintenant/,
  publicationModeLaterRadio: /Publier plus tard/,
  publicationDateInput: 'Date *',
  publicationTimeSelect: 'Heure *',
  submitInstantOfferButton: 'Publier l’offre',
  submitScheduledOfferButton: 'Programmer l’offre',
}

const ERROR_MESSAGES = {
  publicationDateIsRequired: /Veuillez sélectionner une date de publication/,
  publicationTimeIsRequired: /Veuillez sélectionner une heure de publication/,
  publicationDateMustBeInFuture: /Veuillez indiquer une date dans le futur/,
  publicationDateMustBeWithinTwoYears:
    /Veuillez indiquer une date dans les 2 ans à venir/,
}

const renderSummaryScreen = ({
  contextValue,
  mode = OFFER_WIZARD_MODE.CREATION,
  path,
}: {
  contextValue: IndividualOfferContextValues
  mode?: OFFER_WIZARD_MODE
  path?: string
}) => {
  const controlledPath =
    path ??
    getIndividualOfferPath({
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode,
    })
  const element = (
    <IndividualOfferContext.Provider value={contextValue}>
      <SummaryScreen />
    </IndividualOfferContext.Provider>
  )
  const component = (
    <Routes>
      <Route path={controlledPath} element={element} />
    </Routes>
  )

  const overrides = {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: [controlledPath],
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
  }

  return renderWithProviders(component, overrides)
}

describe('SummaryScreen', () => {
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
    const categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    const subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: ['ean'],
        canBeDuo: true,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    contextValue = individualOfferContextValuesFactory({
      categories,
      offer: getIndividualOfferFactory({ id: 1 }),
      subCategories,
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Form', () => {
    const inOneMonth = set(add(new Date(), { months: 1 }), {
      hours: 10,
      minutes: 0,
    })

    it("should validate publication date and time when it's a scheduled publication", async () => {
      renderSummaryScreen({ contextValue })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )
      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(
        await screen.findByText(ERROR_MESSAGES.publicationDateIsRequired)
      ).toBeVisible()
      expect(
        await screen.findByText(ERROR_MESSAGES.publicationTimeIsRequired)
      ).toBeVisible()

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(
        LABELS.publicationTimeSelect
      )

      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )

      expect(
        screen.queryByText(ERROR_MESSAGES.publicationDateIsRequired)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(ERROR_MESSAGES.publicationDateMustBeInFuture)
      ).toBeVisible()
      expect(
        screen.queryByText(ERROR_MESSAGES.publicationTimeIsRequired)
      ).toBeVisible()

      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inOneMonth, 'HH:mm')
      )

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: contextValue.offer!.id,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })

    it("should require publication date to be in the future when it's a scheduled publication", async () => {
      const yesterday = set(sub(new Date(), { days: 1 }), {
        hours: 10,
        minutes: 0,
      })

      renderSummaryScreen({ contextValue })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(
        LABELS.publicationTimeSelect
      )

      await userEvent.type(
        publicationDateInput,
        format(yesterday, 'yyyy-MM-dd')
      )
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(yesterday, 'HH:mm')
      )

      expect(
        await screen.findByText(ERROR_MESSAGES.publicationDateMustBeInFuture)
      ).toBeVisible()

      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )

      // -----------------------------------------------------------------------
      // Hack to force value update within RTL
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inOneMonth, 'HH:mm')
      )
      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )
      // -----------------------------------------------------------------------

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: contextValue.offer!.id,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })

    it("should require publication date to be within two years when it's a scheduled publication", async () => {
      const inMoreThanTwoYears = set(add(new Date(), { months: 25 }), {
        hours: 10,
        minutes: 0,
      })

      renderSummaryScreen({ contextValue })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(
        LABELS.publicationTimeSelect
      )

      await userEvent.type(
        publicationDateInput,
        format(inMoreThanTwoYears, 'yyyy-MM-dd')
      )
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inMoreThanTwoYears, 'HH:mm')
      )

      expect(
        await screen.findByText(
          ERROR_MESSAGES.publicationDateMustBeWithinTwoYears
        )
      ).toBeVisible()

      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )

      // -----------------------------------------------------------------------
      // Hack to force value update within RTL
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inOneMonth, 'HH:mm')
      )
      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )
      // -----------------------------------------------------------------------

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: contextValue.offer!.id,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })
  })
})
