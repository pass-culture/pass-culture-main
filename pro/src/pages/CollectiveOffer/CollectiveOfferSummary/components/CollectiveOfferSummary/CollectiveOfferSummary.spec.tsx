import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  EacFormat,
  OfferContactFormEnum,
} from 'apiClient/v1'
import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { expect } from 'vitest'

import {
  CollectiveOfferSummary,
  CollectiveOfferSummaryProps,
} from './CollectiveOfferSummary'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getVenue: vi.fn(),
  },
}))

const renderCollectiveOfferSummary = (
  props: CollectiveOfferSummaryProps,
  overrides?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferSummary {...props} />, overrides)
}

describe('CollectiveOfferSummary', () => {
  let props: CollectiveOfferSummaryProps
  beforeEach(() => {
    const offer = getCollectiveOfferFactory()
    props = {
      offer,
    }
  })
  it('should show banner if generate from publicApi', async () => {
    const offer = getCollectiveOfferFactory({
      isPublicApi: true,
      provider: { name: 'Mollat' },
    })

    renderCollectiveOfferSummary({
      ...props,
      offer,
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText('Offre synchronisée avec Mollat')
    ).toBeInTheDocument()
  })

  it('should not see edit button if offer from publicApi', async () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: true })

    renderCollectiveOfferSummary({
      ...props,
      offer,
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.queryAllByRole('link', { name: 'Modifier' })).toHaveLength(0)
  })

  it('should display national program', async () => {
    renderCollectiveOfferSummary(props)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Dispositif national :')).toBeInTheDocument()
    expect(screen.getByText('Collège au cinéma')).toBeInTheDocument()
  })

  it('should display format', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: {
        ...props.offer,
        formats: [EacFormat.PROJECTION_AUDIOVISUELLE, EacFormat.CONCERT],
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(
      screen.getByText('Projection audiovisuelle, Concert')
    ).toBeInTheDocument()
  })

  it('should display the date and time of the offer', async () => {
    const offer = getCollectiveOfferTemplateFactory({
      dates: { start: '2023-10-24T09:14:00', end: '2023-10-24T09:16:00' },
    })
    renderCollectiveOfferSummary({ ...props, offer })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const title = screen.getByRole('heading', {
      name: 'Date et heure',
    })

    expect(title).toBeInTheDocument()
  })

  it('should display the custom contact details', async () => {
    const offer = getCollectiveOfferTemplateFactory({
      contactEmail: 'email@test.co',
      contactPhone: '00000000',
      contactForm: OfferContactFormEnum.FORM,
    })
    renderCollectiveOfferSummary({ ...props, offer })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('email@test.co')).toBeInTheDocument()
    expect(screen.getByText('00000000')).toBeInTheDocument()
    expect(
      screen.getByText('Le formulaire standard Pass Culture')
    ).toBeInTheDocument()
  })

  it('should display the custom contact custom url', async () => {
    const offer = getCollectiveOfferTemplateFactory({
      contactUrl: 'http://www.form.com',
    })
    renderCollectiveOfferSummary({ ...props, offer })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('http://www.form.com')).toBeInTheDocument()
  })

  it('should not display the edition button when there is no edition link', async () => {
    renderCollectiveOfferSummary({ ...props, offerEditLink: undefined })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should display the edition buttons when the template offer can be edited', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
      }),
      offerEditLink: '123',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should not display the edition buttons when the template offer cannot be edited', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      }),
      offerEditLink: '123',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should not display the edition buttons when the bookable offer cannot be edited', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
      offerEditLink: '123',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should display one edition button when the offer description is editable', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      }),
      offerEditLink: '123',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.queryByRole('link', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should display two edition buttons when the offer description and price are editable', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(2)
  })

  it('should display two edition buttons when the offer description and dates are editable', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(2)
  })

  it('should display three edition buttons when the offer description, dates and institution are editable', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
          CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
      visibilityEditLink: '345',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(3)
  })
})
