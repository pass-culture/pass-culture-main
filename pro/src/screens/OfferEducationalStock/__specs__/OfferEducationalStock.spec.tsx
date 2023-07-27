import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, addMinutes, format } from 'date-fns'
import React from 'react'

import { StudentLevels } from 'apiClient/adage'
import { Events } from 'core/FirebaseEvents/constants'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational'
import * as useAnalytics from 'hooks/useAnalytics'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalStock, {
  OfferEducationalStockProps,
} from '../OfferEducationalStock'

const defaultProps: OfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: collectiveOfferFactory({}),
  onSubmit: vi.fn(),
  mode: Mode.CREATION,
}

const tomorrow = addDays(new Date(), 1)
const initialValuesNotEmpty = {
  ...DEFAULT_EAC_STOCK_FORM_VALUES,
  eventDate: format(tomorrow, FORMAT_ISO_DATE_ONLY),
  eventTime: format(addMinutes(tomorrow, 15), FORMAT_HH_mm),
  bookingLimitDatetime: '2023-03-30',
  numberOfPlaces: 10,
  totalPrice: 100,
  priceDetail: 'Détail du prix',
}

const mockedUsedNavigate = vi.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedUsedNavigate,
}))

describe('OfferEducationalStock', () => {
  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        eventDate: '2022-02-10',
        eventTime: '00:00',
        bookingLimitDatetime: '2022-02-10',
        numberOfPlaces: 10,
        totalPrice: 100,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.CLASSIC,
      },
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    screen.getByText('Date et prix')
  })

  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByText('Offre importée automatiquement')
    ).toBeInTheDocument()
  })

  it('should not disable price and place when offer status is reimbursment', () => {
    const offer = collectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.READ_ONLY,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    const priceInput = screen.getByLabelText('Prix global TTC')
    const placeInput = screen.getByLabelText('Nombre de places')

    expect(priceInput).not.toBeDisabled()
    expect(placeInput).not.toBeDisabled()
  })

  it('should call submit callback when clicking next step with valid form data', async () => {
    const offer = collectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: initialValuesNotEmpty,
      mode: Mode.CREATION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', { name: 'Étape suivante' })
    await userEvent.click(submitButton)

    expect(testProps.onSubmit).toHaveBeenCalled()
  })

  describe('wrong students modal', () => {
    it('should navigate to offer creation if user click modify participants', async () => {
      const offer = collectiveOfferFactory({
        id: 1,
        students: [StudentLevels.COLL_GE_6E, StudentLevels.COLL_GE_5E],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })
      await userEvent.click(submitButton)

      const modifyStudentsButton = screen.getByRole('button', {
        name: 'Modifier les participants',
      })
      await userEvent.click(modifyStudentsButton)

      expect(mockedUsedNavigate).toHaveBeenCalledWith(
        '/offre/collectif/1/creation'
      )
    })

    it('should navigate to offer creation if user click modify participants', async () => {
      const offer = collectiveOfferFactory({
        id: 1,
        students: [StudentLevels.COLL_GE_6E, StudentLevels.COLL_GE_5E],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
        mode: Mode.EDITION,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Enregistrer',
      })
      await userEvent.click(submitButton)

      const modifyStudentsButton = screen.getByRole('button', {
        name: 'Modifier les participants',
      })
      await userEvent.click(modifyStudentsButton)

      expect(mockedUsedNavigate).toHaveBeenCalledWith(
        '/offre/collectif/1/edition'
      )
    })

    it('should call onSubmit  if user click create offer', async () => {
      const offer = collectiveOfferFactory({
        id: 1,
        students: [
          StudentLevels.COLL_GE_6E,
          StudentLevels.COLL_GE_5E,
          StudentLevels.COLL_GE_4E,
        ],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })
      await userEvent.click(submitButton)

      const deleteWrongStudents = screen.getByRole('button', {
        name: 'Enlever les 6e et 5e',
      })
      await userEvent.click(deleteWrongStudents)

      expect(testProps.onSubmit).toHaveBeenCalled()
    })

    it('should close modal if user click modify date', async () => {
      const offer = collectiveOfferFactory({
        id: 1,
        students: [
          StudentLevels.COLL_GE_6E,
          StudentLevels.COLL_GE_5E,
          StudentLevels.COLL_GE_4E,
        ],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })
      await userEvent.click(submitButton)

      const modifyDate = screen.getByRole('button', {
        name: 'Modifier la date',
      })
      await userEvent.click(modifyDate)

      expect(
        screen.queryByText('Cette offre ne peut pas s’adresser aux 6e et 5e')
      ).not.toBeInTheDocument()
    })
    it('should log event when wrong students modal is displayed with only wrong students', async () => {
      const mockLogEvent = vi.fn()
      vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        ...jest.requireActual('hooks/useAnalytics'),
        logEvent: mockLogEvent,
      }))

      const offer = collectiveOfferFactory({
        id: 1,
        students: [StudentLevels.COLL_GE_6E, StudentLevels.COLL_GE_5E],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })
      await userEvent.click(submitButton)

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.EAC_WRONG_STUDENTS_MODAL_OPEN,
        { from: '/', hasOnly6eAnd5eStudents: true }
      )
    })

    it('should log event when wrong students modal is displayed with not only wrong students', async () => {
      const mockLogEvent = vi.fn()
      vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        ...jest.requireActual('hooks/useAnalytics'),
        logEvent: mockLogEvent,
      }))

      const offer = collectiveOfferFactory({
        id: 1,
        students: [StudentLevels.COLL_GE_6E, StudentLevels.LYC_E_SECONDE],
      })
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: initialValuesNotEmpty,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })
      await userEvent.click(submitButton)

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.EAC_WRONG_STUDENTS_MODAL_OPEN,
        { from: '/', hasOnly6eAnd5eStudents: false }
      )
    })

    it('should render for offer with a stock', async () => {
      const offer = collectiveOfferFactory()

      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        initialValues: {
          ...DEFAULT_EAC_STOCK_FORM_VALUES,
          eventDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
          eventTime: format(new Date(), FORMAT_ISO_DATE_ONLY),
          bookingLimitDatetime: '2023-03-30',
          numberOfPlaces: 10,
          totalPrice: 100,
        },
      }

      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const submitButton = screen.getByRole('button', {
        name: 'Étape suivante',
      })

      await userEvent.click(submitButton)

      screen.getByText("L'heure doit être postérieure à l'heure actuelle")
    })
  })
})
