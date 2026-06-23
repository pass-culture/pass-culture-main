import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { ExposureEventType } from '@/apiClient/v1'
import { getOfferExposureFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferExposureTimeline } from './OfferExposureTimeline'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferExposure: vi.fn(),
  },
}))

const defaultExposureEvents = [
  {
    type: ExposureEventType.HEADLINE,
    name: null,
    startDate: '2026-02-14T00:00:00Z',
    endDate: '2026-03-04T00:00:00Z',
    viewsOnPeriod: 30,
  },
  {
    type: ExposureEventType.HIGHLIGHT,
    name: 'Journées Européennes du Patrimoine',
    startDate: '2026-02-02T00:00:00Z',
    endDate: '2026-02-26T00:00:00Z',
    viewsOnPeriod: 10,
  },
  {
    type: ExposureEventType.PRO_ADVICE,
    name: null,
    startDate: '2025-12-23T00:00:00Z',
    endDate: null,
    viewsOnPeriod: null,
  },
]

function renderOfferExposureTimeline(
  creationDate = '2025-12-03T00:00:00Z',
  departmentCode = '75'
) {
  return renderWithProviders(
    <OfferExposureTimeline
      offerId={1}
      creationDate={creationDate}
      departmentCode={departmentCode}
    />
  )
}

describe('OfferExposureTimeline', () => {
  beforeEach(() => {
    // Only fake `Date` so Testing Library's async helpers keep working
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-06-23T00:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should render each enhancement event', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({ events: defaultExposureEvents })
    )

    renderOfferExposureTimeline()

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const steps = screen.getAllByRole('listitem')
    expect(steps).toHaveLength(3)
    expect(steps[0]).toHaveTextContent(
      '14/02 - 04/03 : Mise à la une de votre offre'
    )
    expect(steps[0]).toHaveTextContent('+30 consultations sur cette période')
    expect(steps[1]).toHaveTextContent(
      '02/02 - 26/02 : Lien de votre offre au temps fort “Journées Européennes du Patrimoine”'
    )
    expect(steps[2]).toHaveTextContent('23/12 : Ajout d’une recommandation')
  })

  it('should display dates in the offer department timezone', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({ events: defaultExposureEvents })
    )

    renderOfferExposureTimeline('2025-12-03T00:00:00Z', '972')

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const steps = screen.getAllByRole('listitem')
    expect(steps[0]).toHaveTextContent(
      '13/02 - 03/03 : Mise à la une de votre offre'
    )
    expect(steps[1]).toHaveTextContent(
      '01/02 - 25/02 : Lien de votre offre au temps fort “Journées Européennes du Patrimoine”'
    )
    expect(steps[2]).toHaveTextContent('22/12 : Ajout d’une recommandation')
  })

  it('should not display the views line when there are no views', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({
        events: [
          {
            type: ExposureEventType.HEADLINE,
            name: null,
            startDate: '2026-02-14T00:00:00Z',
            endDate: '2026-03-04T00:00:00Z',
            viewsOnPeriod: 0,
          },
        ],
      })
    )

    renderOfferExposureTimeline()

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const [step] = screen.getAllByRole('listitem')
    expect(step).toHaveTextContent(
      '14/02 - 04/03 : Mise à la une de votre offre'
    )
    expect(step).not.toHaveTextContent(/consultation/)
  })

  it('should handle ongoing events with end dates', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({
        events: [
          {
            type: ExposureEventType.HEADLINE,
            name: null,
            startDate: '2026-02-14T00:00:00Z',
            endDate: '2026-12-04T00:00:00Z',
            viewsOnPeriod: 30,
          },
        ],
      })
    )

    renderOfferExposureTimeline()

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const [step] = screen.getAllByRole('listitem')
    expect(step).toHaveTextContent('14/02 : Mise à la une de votre offre')
    expect(step).not.toHaveTextContent(/consultation/)
  })

  it('should not render anything when there is no event', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({ events: [] })
    )

    const { container } = renderOfferExposureTimeline()

    await waitFor(() => {
      expect(api.getOfferExposure).toHaveBeenCalled()
    })

    expect(
      screen.queryByRole('heading', { name: 'Vos dernières actions' })
    ).not.toBeInTheDocument()
    expect(container).toBeEmptyDOMElement()
  })

  it('should add a creation step when there are fewer than 3 events', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({
        events: [
          {
            type: ExposureEventType.HEADLINE,
            name: null,
            startDate: '2026-02-14T00:00:00Z',
            endDate: '2026-03-04T00:00:00Z',
            viewsOnPeriod: 30,
          },
        ],
      })
    )

    renderOfferExposureTimeline('2025-12-03T00:00:00Z')

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const steps = screen.getAllByRole('listitem')
    expect(steps).toHaveLength(2)
    expect(steps[1]).toHaveTextContent('03/12 : Création de votre offre')
  })

  it('should not add a creation step when there are 3 events', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({ events: defaultExposureEvents })
    )

    renderOfferExposureTimeline('2025-12-03T00:00:00Z')

    expect(
      await screen.findByRole('heading', { name: 'Vos dernières actions' })
    ).toBeInTheDocument()

    const steps = screen.getAllByRole('listitem')
    expect(steps).toHaveLength(3)
    for (const step of steps) {
      expect(step).not.toHaveTextContent('Création de votre offre')
    }
  })
})
