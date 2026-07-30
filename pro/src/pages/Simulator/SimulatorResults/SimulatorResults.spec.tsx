import { screen, waitFor, within } from '@testing-library/react'
import { noop } from 'commons/utils/noop'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ActivityNotOpenToPublic,
  EligibilityDocument,
  SignupSimulationMessageLevel,
  SignupSimulationMessageType,
  TargetAudience,
} from 'apiClient/v1'
import { SimulatorResults } from './SimulatorResults'

const contextValue = {
  siret: '123 456 789 01234',
  setSiret: vi.fn(),
  targetAudiences: {
    individual: true,
    collective: true,
  },
  setTargetAudiences: vi.fn(),
  openToPublic: 'true',
  setOpenToPublic: noop,
  activity: ActivityNotOpenToPublic.ARTISTIC_COMPANY,
  setActivity: vi.fn(),
}

const renderSimulatorResult = (contextOverride = {}) => {
  return renderWithProviders(
    <SimulatorContext.Provider value={{ ...contextValue, ...contextOverride }}>
      <SimulatorResults />
    </SimulatorContext.Provider>,
    { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
  )
}

describe('<SimulatorResults />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorResults />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it.each([
    {
      inputTargets: { individual: true, collective: true },
      expectedTargets: [TargetAudience.INDIVIDUAL, TargetAudience.COLLECTIVE],
    },
    {
      inputTargets: { individual: true, collective: false },
      expectedTargets: [TargetAudience.INDIVIDUAL],
    },
    {
      inputTargets: { individual: false, collective: true },
      expectedTargets: [TargetAudience.COLLECTIVE],
    },
  ])(
    'should call the simulateSignup endpoint with the following targets: $expectedTargets',
    async ({ inputTargets, expectedTargets }) => {
      vi.spyOn(api, 'simulateSignup').mockResolvedValueOnce({
        eligibilityDocuments: [EligibilityDocument.PRICES],
        messages: [],
      })
      renderSimulatorResult({ targetAudiences: inputTargets })

      await waitFor(() => {
        expect(api.simulateSignup).toHaveBeenCalledExactlyOnceWith({
          body: {
            activity: ActivityNotOpenToPublic.ARTISTIC_COMPANY,
            isOpenToPublic: true,
            siret: '12345678901234',
            targets: expectedTargets,
          },
        })
      })
    }
  )

  it.each([
    {
      input: {
        doc: EligibilityDocument.PRICES,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Grille tarifaire',
        bannerRole: 'alert',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.WEBSITE,
        msgType: SignupSimulationMessageType.COLLECTIVE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Un site internet ou page de réseau social',
        bannerRole: 'alert',
        bannerTitle: /votre dépôt de dossier ADAGE/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.RESUME_OR_PORTFOLIO,
        msgType: SignupSimulationMessageType.UNUSUAL_APE_CODE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'CV et/ou portfolio',
        bannerRole: 'alert',
        bannerTitle: /activités fixées par arrêté sont éligibles/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.DIPLOMAS,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.INFO,
      },
      expected: {
        documentTitle: 'Diplôme(s)',
        bannerRole: 'status',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
        msgType: SignupSimulationMessageType.COLLECTIVE,
        msgLevel: SignupSimulationMessageLevel.INFO,
      },
      expected: {
        documentTitle: 'Diplôme et/ou attestation dans les métiers du son',
        bannerRole: 'status',
        bannerTitle: /votre dépôt de dossier ADAGE/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.PRICES,
        msgType: SignupSimulationMessageType.UNUSUAL_APE_CODE,
        msgLevel: SignupSimulationMessageLevel.INFO,
      },
      expected: {
        documentTitle: 'Grille tarifaire',
        bannerRole: 'status',
        bannerTitle: /activités fixées par arrêté sont éligibles/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.SHOP_PICTURES,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Photos du point de vente',
        bannerRole: 'alert',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.SOUND_STUDIO_PICTURES,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Photos des locaux et du matériel',
        bannerRole: 'alert',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.CRIMINAL_RECORDS,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Extrait de casier judiciaire (bulletin n°3)',
        bannerRole: 'alert',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
    {
      input: {
        doc: EligibilityDocument.DESCRIPTION,
        msgType: SignupSimulationMessageType.BOOKSTORE,
        msgLevel: SignupSimulationMessageLevel.ALERT,
      },
      expected: {
        documentTitle: 'Une description détaillée de vos offres',
        bannerRole: 'alert',
        bannerTitle: /disposer d'un point de vente physique/,
      },
    },
  ])(
    'should render with document $input.doc and message $input.msgType with level $input.msgLevel',
    async ({
      input: { doc, msgLevel, msgType },
      expected: { documentTitle, bannerRole, bannerTitle },
    }) => {
      vi.spyOn(api, 'simulateSignup').mockResolvedValueOnce({
        eligibilityDocuments: [doc],
        messages: [{ type: msgType, level: msgLevel }],
      })
      renderSimulatorResult()

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { level: 2, name: documentTitle })
        ).toBeVisible()
      })

      const messageBanner = screen.getByRole(bannerRole)
      expect(messageBanner).toBeVisible()
      expect(within(messageBanner).getByText(bannerTitle)).toBeVisible()
    }
  )
})
