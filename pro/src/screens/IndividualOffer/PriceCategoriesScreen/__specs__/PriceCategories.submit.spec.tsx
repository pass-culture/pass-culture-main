import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import {
  getIndividualOfferFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  PriceCategoriesScreen,
  PriceCategoriesScreenProps,
} from '../PriceCategoriesScreen'

const renderPriceCategories = (
  props: PriceCategoriesScreenProps,
  url = generatePath(
    getIndividualOfferPath({
      step: OFFER_WIZARD_STEP_IDS.TARIFS,
      mode: OFFER_WIZARD_MODE.CREATION,
    }),
    { offerId: 'AA' }
  )
) =>
  renderWithProviders(
    <>
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map((mode) => (
          <Route
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.TARIFS,
              mode,
            })}
            element={<PriceCategoriesScreen {...props} />}
            key={mode}
          />
        ))}
      </Routes>
      <Notification />
    </>,
    { initialRouterEntries: [url] }
  )

describe('PriceCategories', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffer').mockResolvedValue(getIndividualOfferFactory())
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'postPriceCategories').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should notify and submit when clicking on Enregistrer et continuer in creation', async () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({ hasStocks: false }),
    })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    await waitFor(() => {
      expect(api.patchOffer).toHaveBeenCalled()
    })
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should display price modification modal', async () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({
        bookingsCount: 0,
        priceCategories: [priceCategoryFactory({ id: 666 })],
      }),
    })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      await screen.findByText(
        'Cette modification de tarif s’appliquera à l’ensemble des dates qui y sont associées.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Le tarif restera inchangé pour les personnes ayant déjà réservé cette offre.'
      )
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer la modification'))

    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should display price modification modal with booking', async () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({
        priceCategories: [priceCategoryFactory({ id: 666 })],
        bookingsCount: 10,
      }),
    })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      await screen.findByText(
        'Cette modification de tarif s’appliquera à l’ensemble des dates qui y sont associées.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Le tarif restera inchangé pour les personnes ayant déjà réservé cette offre.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer la modification'))

    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify and submit when clicking on Enregistrer les modifications in edition', async () => {
    renderPriceCategories(
      { offer: getIndividualOfferFactory({ hasStocks: false }) },
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify an error when submit fail', async () => {
    vi.spyOn(api, 'postPriceCategories').mockRejectedValue({})

    renderPriceCategories(
      { offer: getIndividualOfferFactory({ hasStocks: false }) },
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      await screen.findByText(
        'Une erreur est survenue lors de la mise à jour de votre tarif'
      )
    ).toBeInTheDocument()
  })

  it('should notify an error when submit fail because offer was virtual without url', async () => {
    vi.spyOn(api, 'postPriceCategories').mockRejectedValue({
      message: 'oups',
      name: 'ApiError',
      body: { url: 'broken virtual offer !' },
    })

    renderPriceCategories(
      { offer: getIndividualOfferFactory({ hasStocks: false }) },
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne *'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      await screen.findByText(
        'Vous n’avez pas renseigné l’URL d’accès à l’offre dans la page Informations pratiques.'
      )
    ).toBeInTheDocument()
  })
})
