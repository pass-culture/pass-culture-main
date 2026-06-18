import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { expect } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import type { StructureDataBodyModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as getSiretData from '@/commons/core/Venue/utils/getSiretData'
import { structureDataBodyModelFactory } from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { SiretInputForm } from '@/components/SiretInputForm/SiretInputForm'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { ApiError } from 'apiClient/compat'

// Mock l’appel à https://data.geopf.fr/geocodage/search/?limit=${limit}&q=${address}
// Appel fait dans getDataFromAddress
vi.mock('@/apiClient/adresse/apiAdresse', () => ({
  getDataFromAddressParts: () =>
    Promise.resolve([
      {
        address: 'name',
        city: 'city',
        id: 'id',
        latitude: 0,
        longitude: 0,
        label: 'label',
        postalCode: 'postcode',
      },
    ]),
}))
// Disable memoization because getSiretData value needs to change
vi.mock('@/commons/utils/memoize', () => ({
  memoize: (func: unknown) => func,
}))

const mockHandleSiretData = vi.fn()
const renderInputForm = (initialValues = DEFAULT_OFFERER_FORM_VALUES) => {
  return renderWithProviders(
    <>
      <SiretInputForm
        submitElement={(isSubmitting) => (
          <button type="submit" disabled={isSubmitting}>
            submit
          </button>
        )}
        checkShouldSubmit={() => true}
        initialValues={initialValues}
        handleSiretData={mockHandleSiretData}
      />
      <SnackBarContainer />
    </>
  )
}
describe('<SiretInputForm />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
    vi.spyOn(api, 'checkStructure').mockResolvedValue()
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderInputForm()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render component', async () => {
    renderInputForm()

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Renseignez le SIRET de la structure à laquelle vous êtes rattaché.'
    )
    expect(
      await screen.findByRole('button', { name: 'submit' })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('link', {
        name: /Modifier la visibilité de mon SIRET/,
      })
    ).not.toBeInTheDocument()

    expect(screen.getByRole('status')).toHaveTextContent(
      /Vous êtes un équipement d’une collectivité ou d’un établissement public \?/
    )

    expect(
      screen.getByRole('link', { name: /En savoir plus/ })
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-'
    )

    expect(
      screen.getByText('Vous ne connaissez pas votre SIRET ?')
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', {
        name: /Consultez l'Annuaire des Entreprises/,
      })
    ).toHaveAttribute('href', 'https://annuaire-entreprises.data.gouv.fr/')
  })

  it('should continue submit when no api error', async () => {
    renderInputForm()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    expect(api.getStructureData).toHaveBeenCalledOnce()

    expect(screen.getByRole('alert')).not.toHaveTextContent(
      "Le SIRET n'existe pas"
    )
    expect(mockHandleSiretData).toHaveBeenCalled()
  })

  it('should not submit when check is false', async () => {
    const mockBeforeFalse = vi.fn().mockImplementation(() => false)
    renderWithProviders(
      <>
        <SiretInputForm
          submitElement={(isSubmitting) => (
            <button type="submit" disabled={isSubmitting}>
              submit
            </button>
          )}
          checkShouldSubmit={mockBeforeFalse}
          initialValues={DEFAULT_OFFERER_FORM_VALUES}
          handleSiretData={mockHandleSiretData}
        />
        <SnackBarContainer />
      </>
    )

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    expect(screen.getByRole('alert')).not.toHaveTextContent(
      "Le SIRET n'existe pas"
    )

    expect(mockBeforeFalse).toHaveBeenCalled()
    expect(mockHandleSiretData).not.toHaveBeenCalled()
    expect(api.getStructureData).not.toHaveBeenCalled()
  })

  it('should not continue submit on api error', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: ["Le SIRET n'existe pas"],
          },
        } as ApiResult,
        ''
      )
    )

    renderInputForm()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    expect(api.getStructureData).toHaveBeenCalledOnce()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        "Le SIRET n'existe pas"
      )
    })
    expect(api.getStructureData).toHaveBeenCalled()
    expect(mockHandleSiretData).not.toHaveBeenCalled()
  })

  it('should display BannerInvisibleSiren on error 400 with specific message', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: [
              "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public",
            ],
          },
        } as ApiResult,
        ''
      )
    )
    renderInputForm()

    expect(
      screen.queryByRole('link', {
        name: /Modifier la visibilité de mon SIRET/,
      })
    ).not.toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933367'
    )

    await waitFor(() => {
      expect(
        screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
      ).toHaveValue('12345678933367')
    })
    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    expect(api.getStructureData).toHaveBeenCalled()
    expect(
      screen.getByRole('link', { name: /Modifier la visibilité de mon SIRET/ })
    ).toBeInTheDocument()
  })

  it('should log event when unknown siret link clicked', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderInputForm()
    await userEvent.click(
      screen.getByRole('link', {
        name: /Consultez l'Annuaire des Entreprises/,
      })
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedUnknownSiret')
  })

  it('should display error when offererSiretData is null', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue(
      null as unknown as StructureDataBodyModel
    )
    renderInputForm()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    await waitFor(() => {
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    })
  })

  const lenErrorCondition = ['22223333', '1234567891234567']
  it.each(lenErrorCondition)('should render errors', async (siretValue) => {
    renderInputForm()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      siretValue
    )
    await userEvent.click(screen.getByRole('button', { name: 'submit' }))
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Le SIRET doit comporter 14 caractères'
      )
    })
  })

  it('should handle error that is not an instance of Error', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockRejectedValue('string error')
    renderInputForm()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    // When error is not an instance of Error, nothing happens in the catch block
    // The form should remain visible and no error should be set
    await waitFor(() => {
      expect(
        screen.queryByRole('link', {
          name: /Modifier la visibilité de mon SIRET/,
        })
      ).not.toBeInTheDocument()
    })
  })

  it('should check siret if needed', async () => {
    const checkSiretMock = vi.fn()
    renderWithProviders(
      <>
        <SiretInputForm
          submitElement={(isSubmitting) => (
            <button type="submit" disabled={isSubmitting}>
              submit
            </button>
          )}
          checkShouldSubmit={() => true}
          initialValues={DEFAULT_OFFERER_FORM_VALUES}
          onSiretChecked={checkSiretMock}
        />
        <SnackBarContainer />
      </>
    )

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'submit' }))

    expect(api.getStructureData).not.toHaveBeenCalled()
    expect(api.checkStructure).toHaveBeenCalledOnce()

    expect(mockHandleSiretData).not.toHaveBeenCalled()
    expect(checkSiretMock).toHaveBeenCalled()
  })
})
