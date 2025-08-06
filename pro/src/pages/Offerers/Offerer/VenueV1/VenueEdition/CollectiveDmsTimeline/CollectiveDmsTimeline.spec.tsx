import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { DMSApplicationForEAC, DMSApplicationstatus } from '@/apiClient//v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveDmsTimeline } from './CollectiveDmsTimeline'

const mockLogEvent = vi.fn()

interface CollectiveDmsTimelineProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
  adageInscriptionDate?: string | null
  offererId?: number
}

const renderCollectiveDmsTimeline = (
  {
    collectiveDmsApplication,
    hasAdageId = false,
    hasAdageIdForMoreThan30Days = false,
    adageInscriptionDate = null,
  }: CollectiveDmsTimelineProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
      hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
      adageInscriptionDate={adageInscriptionDate}
    />,
    options
  )
}

interface TestCaseProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
  expectedLabel: string
}

describe('CollectiveDmsTimeline', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('@/app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))
  })

  const testCases: TestCaseProps[] = [
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.EN_CONSTRUCTION,
      },
      expectedLabel: 'Votre dossier a été déposé',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.EN_INSTRUCTION,
      },
      expectedLabel: 'Votre dossier est en cours d’instruction',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.ACCEPTE,
      },
      expectedLabel: 'Votre demande de référencement a été acceptée',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.ACCEPTE,
      },
      hasAdageId: true,
      expectedLabel:
        'Votre structure a été référencée dans ADAGE par les équipes du Ministère de l’Education Nationale',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.REFUSE,
      },
      expectedLabel: 'Votre demande de référencement a été refusée',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.SANS_SUITE,
      },
      expectedLabel: 'Votre demande de référencement a été classée sans suite',
    },
  ]
  it.each(testCases)(
    'should render %s status',
    ({
      collectiveDmsApplication,
      hasAdageId,
      hasAdageIdForMoreThan30Days,
      expectedLabel,
    }) => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication,
        hasAdageId,
        hasAdageIdForMoreThan30Days,
      })
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )

  const dmsStates = [
    DMSApplicationstatus.EN_CONSTRUCTION,
    DMSApplicationstatus.EN_INSTRUCTION,
    DMSApplicationstatus.ACCEPTE,
    DMSApplicationstatus.REFUSE,
    DMSApplicationstatus.SANS_SUITE,
  ]
  it.each(dmsStates)(
    'should log event on click dms link',
    async (dmsState: DMSApplicationstatus) => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultDMSApplicationForEAC,
          state: dmsState,
        },
      })
      const dmsLink = screen.getByRole('link', {
        name: /Consulter ma messagerie sur Démarches Simplifiées/,
      })

      dmsLink.addEventListener('click', (e) => {
        e.preventDefault()
      })

      await userEvent.click(dmsLink)
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EAC_DMS_LINK, {
        from: '/',
        dmsApplicationStatus: dmsState,
      })
    }
  )

  it('should display dates for status', () => {
    const collectiveDmsApplication = {
      application: 11922836,
      buildDate: '2023-03-23T15:08:35Z',
      depositDate: '2024-03-23T15:08:33Z',
      lastChangeDate: '2023-03-26T15:08:35Z',
      instructionDate: '2025-03-24T15:08:33Z',
      processingDate: '2025-03-27T15:08:33Z',
      procedure: 123,
      state: DMSApplicationstatus.ACCEPTE,
      venueId: 33,
    }

    renderCollectiveDmsTimeline({
      collectiveDmsApplication: collectiveDmsApplication,
      hasAdageId: true,
      hasAdageIdForMoreThan30Days: false,
      adageInscriptionDate: '2025-03-28T15:08:33Z',
    })

    expect(screen.getByText(/23 mars 2023/)).toBeInTheDocument()
    expect(screen.getByText(/24 mars 2025/)).toBeInTheDocument()
    expect(screen.getByText(/27 mars 2025/)).toBeInTheDocument()
    expect(screen.getByText(/28 mars 2025/)).toBeInTheDocument()
  })
})
