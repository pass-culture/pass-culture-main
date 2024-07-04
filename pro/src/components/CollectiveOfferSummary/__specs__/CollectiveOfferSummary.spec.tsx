import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { EacFormat, OfferContactFormEnum } from 'apiClient/v1'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import {
  CollectiveOfferSummary,
  CollectiveOfferSummaryProps,
} from '../CollectiveOfferSummary'
import { DEFAULT_RECAP_VALUE } from '../components/constants'

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

  it('should display format when ff is active', async () => {
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

  it('should display defaut format value when null and ff is active', async () => {
    renderCollectiveOfferSummary({
      ...props,
      offer: {
        ...props.offer,
        formats: null,
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(screen.getAllByText(DEFAULT_RECAP_VALUE)[0]).toBeInTheDocument()
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
})
