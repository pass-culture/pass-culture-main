import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { CollectiveOfferAllowedAction } from '@/apiClient/v1'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { MandatoryCollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferEditionInstitution } from '../CollectiveOfferEditionInstitution'

const renderCollectiveOfferEditionInstitution = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps = defaultProps,
  storeOverride?: any
) => {
  return renderWithProviders(<CollectiveOfferEditionInstitution {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          allowedOnAdage: true,
        }),
      },
      ...storeOverride,
    },
  })
}

const defaultProps = {
  offer: getCollectiveOfferFactory({
    allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION],
  }),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferEditionInstitution', () => {
  const institution = {
    id: 12,
    name: 'Institution 1',
    postalCode: '91190',
    city: 'Gif-sur-Yvette',
    institutionType: 'Collège',
    phoneNumber: '',
    institutionId: 'ABCDEF11',
  }

  beforeEach(() => {
    vi.spyOn(api, 'getEducationalInstitutions').mockResolvedValue({
      educationalInstitutions: [institution],
      page: 1,
      pages: 1,
      total: 1,
    })
    vi.spyOn(
      api,
      'getAutocompleteEducationalRedactorsForUai'
    ).mockResolvedValue([])
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferEditionInstitution(
      '/offre/A1/collectif/etablissement'
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render collective offer institution form', async () => {
    renderCollectiveOfferEditionInstitution('/offre/A1/collectif/etablissement')

    expect(
      await screen.findByRole('heading', {
        name: /Modifier l'offre/,
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(api.getEducationalInstitutions).toHaveBeenCalledOnce()
    })
  })

  it.each([institution, null])(
    'should not fetch institutions or redactors in read-only mode with institution %j',
    async (institution) => {
      renderCollectiveOfferEditionInstitution(
        '/offre/A1/collectif/etablissement',
        {
          ...defaultProps,
          offer: getCollectiveOfferFactory({
            allowedActions: [],
            institution,
            teacher: {
              civility: null,
              firstName: 'Camille',
              lastName: 'Dupont',
              email: 'camille.dupont@example.com',
            },
          }),
        }
      )

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      expect(institutionInput).toBeDisabled()
      await waitFor(() => {
        expect(institutionInput).toHaveValue(
          institution ? 'Collège Institution 1 - Gif-sur-Yvette - ABCDEF11' : ''
        )
      })
      const teacherInput = screen.getByLabelText(
        /Prénom et nom de l’enseignant/
      )
      expect(teacherInput).toBeDisabled()
      expect(teacherInput).toHaveValue('Camille Dupont')
      expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
      expect(api.getEducationalInstitutions).not.toHaveBeenCalled()
      expect(
        api.getAutocompleteEducationalRedactorsForUai
      ).not.toHaveBeenCalled()
    }
  )
})
