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

import { CollectiveOfferCreationInstitution } from '../CollectiveOfferCreationInstitution'

const renderCollectiveOfferCreationInstitution = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  storeOverride?: any
) => {
  return renderWithProviders(
    <CollectiveOfferCreationInstitution {...props} />,
    {
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
    }
  )
}

const defaultProps = {
  offer: getCollectiveOfferFactory({
    allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION],
  }),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferCreationInstitution', () => {
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
    const { container } = renderCollectiveOfferCreationInstitution(
      '/offre/A1/collectif/etablissement',
      defaultProps
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render collective offer institution form', async () => {
    renderCollectiveOfferCreationInstitution(
      '/offre/A1/collectif/etablissement',
      defaultProps
    )

    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(api.getEducationalInstitutions).toHaveBeenCalledOnce()
    })
  })

  it.each([institution, null])(
    'should not fetch institutions or redactors without edit permission with institution %j',
    async (institution) => {
      renderCollectiveOfferCreationInstitution(
        '/offre/A1/collectif/creation/etablissement',
        {
          ...defaultProps,
          offer: getCollectiveOfferFactory({
            allowedActions: [],
            institution,
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
      expect(
        screen.getByLabelText(/Prénom et nom de l’enseignant/)
      ).toBeDisabled()
      expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
      expect(api.getEducationalInstitutions).not.toHaveBeenCalled()
      expect(
        api.getAutocompleteEducationalRedactorsForUai
      ).not.toHaveBeenCalled()
    }
  )
})
