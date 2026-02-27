import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { type DMSApplicationForEAC, DMSApplicationstatus } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveDmsTimeline } from './CollectiveDmsTimeline'
import { CollectiveDmsTimelineVariant } from './types'

const mockLogEvent = vi.fn()

interface CollectiveDmsTimelineProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  adageInscriptionDate?: string | null
  offererId?: number
  variant?: CollectiveDmsTimelineVariant
}

const renderCollectiveDmsTimeline = (
  {
    collectiveDmsApplication,
    hasAdageId = false,
    adageInscriptionDate = null,
    variant = CollectiveDmsTimelineVariant.DEFAULT,
  }: CollectiveDmsTimelineProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
      adageInscriptionDate={adageInscriptionDate}
      variant={variant}
    />,
    options
  )
}

interface TestCaseProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  adageInscriptionDate?: string
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
        'Votre structure a été référencée dans ADAGE par les équipes du ministère de l’Éducation nationale',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.REFUSE,
      },
      expectedLabel:
        'Votre demande de référencement a été refusée pour la part collective',
    },
    {
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.SANS_SUITE,
      },
      expectedLabel: 'Votre demande de référencement a été classée sans suite',
    },
  ]
  it.each(testCases)('should render %s status', ({
    collectiveDmsApplication,
    hasAdageId,
    adageInscriptionDate,
    expectedLabel,
  }) => {
    renderCollectiveDmsTimeline({
      collectiveDmsApplication,
      hasAdageId,
      adageInscriptionDate,
    })
    expect(screen.getByText(expectedLabel)).toBeVisible()
  })

  const dmsStates = [
    DMSApplicationstatus.EN_CONSTRUCTION,
    DMSApplicationstatus.EN_INSTRUCTION,
    DMSApplicationstatus.ACCEPTE,
    DMSApplicationstatus.REFUSE,
    DMSApplicationstatus.SANS_SUITE,
  ]
  it.each(
    dmsStates
  )('should log event on click dms link', async (dmsState: DMSApplicationstatus) => {
    renderCollectiveDmsTimeline({
      collectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: dmsState,
      },
    })
    const dmsLink = screen.getByRole('link', {
      name: /Consulter ma messagerie sur Démarche Numérique/,
    })

    dmsLink.addEventListener('click', (e) => {
      e.preventDefault()
    })

    await userEvent.click(dmsLink)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EAC_DMS_LINK, {
      from: '/',
      dmsApplicationStatus: dmsState,
    })
  })

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
      adageInscriptionDate: '2070-03-28T15:08:33Z',
    })

    expect(screen.getByText(/23 mars 2023/)).toBeVisible()
    expect(screen.getByText(/24 mars 2025/)).toBeVisible()
    expect(screen.getByText(/27 mars 2025/)).toBeVisible()
    expect(screen.getByText(/28 mars 2070/)).toBeVisible()
  })

  describe('when rendered as lite variant', () => {
    it('should display the timeline inside a panel', () => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.EN_INSTRUCTION,
        },
        variant: CollectiveDmsTimelineVariant.LITE,
      })

      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(
        /État d’avancement de votre dossier/
      )
    })

    it('should not render anything when venue has adageId but DMS application is not accepted', () => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.EN_INSTRUCTION,
        },
        hasAdageId: true,
        variant: CollectiveDmsTimelineVariant.LITE,
      })

      expect(
        screen.queryByText(
          /Votre dossier a été validé et vous pouvez dès à présent commencer votre activité avec le pass Culture/
        )
      ).not.toBeInTheDocument()
    })

    it('should display success banner when accepted and processing date is less than 30 days ago', () => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.ACCEPTE,
          processingDate: '2070-04-22T15:08:33Z',
        },
        variant: CollectiveDmsTimelineVariant.LITE,
      })

      expect(
        screen.getByText(
          /Votre dossier a été validé et vous pouvez dès à présent commencer votre activité avec le pass Culture/
        )
      ).toBeVisible()
    })

    it('should not display success banner when accepted and processing date is more than 30 days ago', () => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.ACCEPTE,
          processingDate: '2020-01-01T00:00:00Z',
        },
        variant: CollectiveDmsTimelineVariant.LITE,
      })

      expect(
        screen.queryByText(
          /Votre dossier a été validé et vous pouvez dès à présent commencer votre activité avec le pass Culture/
        )
      ).not.toBeInTheDocument()
    })
  })
})
