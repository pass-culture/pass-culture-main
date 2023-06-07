import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { GetIndividualOfferFactory } from 'utils/apiFactories'
import {
  individualOfferFactory,
  individualStockFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const renderPriceCategories = (
  props: IPriceCategories,
  url = generatePath(
    getOfferIndividualPath({
      step: OFFER_WIZARD_STEP_IDS.TARIFS,
      mode: OFFER_WIZARD_MODE.CREATION,
    }),
    { offerId: 'AA' }
  )
) =>
  renderWithProviders(
    <>
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.TARIFS,
              mode,
            })}
            element={<PriceCategories {...props} />}
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
    jest.spyOn(api, 'getOffer').mockResolvedValue(GetIndividualOfferFactory())
    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest
      .spyOn(api, 'postPriceCategories')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should notify and submit when clicking on Etape suivante in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory() })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify and submit when clicking on Sauvegarder le brouillon in creation', async () => {
    const priceCategory = priceCategoryFactory()
    renderPriceCategories({
      offer: individualOfferFactory({
        priceCategories: [priceCategory],
      }),
    })

    await userEvent.clear(screen.getByLabelText('Prix par personne'))
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalledWith(expect.any(Number), {
      priceCategories: [
        { id: priceCategory.id, label: 'mon label', price: 20 },
      ],
    })
    expect(api.getOffer).toHaveBeenCalled()
  })

  it('should notify and submit when clicking on Etape suivante in draft', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory() },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify and submit when clicking on Sauvegarder le brouillon in draft', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory() },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should display price modification popin', async () => {
    renderPriceCategories(
      {
        offer: individualOfferFactory(
          undefined,
          individualStockFactory({ priceCategoryId: 666, bookingsQuantity: 0 }),
          undefined,
          priceCategoryFactory({ id: 666 })
        ),
      },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      await screen.findByText(
        'Cette modification de tarif s’appliquera à l’ensemble des occurrences qui y sont associées.'
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

  it('should display price modification popin with booking', async () => {
    renderPriceCategories(
      {
        offer: individualOfferFactory(
          undefined,
          individualStockFactory({
            priceCategoryId: 666,
            bookingsQuantity: 17,
          }),
          undefined,
          priceCategoryFactory({ id: 666 })
        ),
      },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      await screen.findByText(
        'Cette modification de tarif s’appliquera à l’ensemble des occurrences qui y sont associées.'
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

  it('should display label modification popin with booking', async () => {
    renderPriceCategories(
      {
        offer: individualOfferFactory(
          undefined,
          individualStockFactory({
            priceCategoryId: 666,
            bookingsQuantity: 17,
          }),
          undefined,
          priceCategoryFactory({ id: 666 })
        ),
      },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.click(screen.getByText('Ajouter un tarif'))

    await userEvent.type(
      screen.getAllByLabelText('Intitulé du tarif')[0],
      'NEW !'
    )
    await userEvent.type(
      screen.getAllByLabelText('Intitulé du tarif')[1],
      'a label'
    )
    await userEvent.type(screen.getAllByLabelText('Prix par personne')[1], '1')
    await userEvent.click(screen.getByText('Étape suivante'))
    expect(
      await screen.findByText(
        'L’intitulé de ce tarif restera inchangé pour les personnes ayant déjà réservé cette offre.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer la modification'))

    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify and submit when clicking on Enregistrer les modifications in edition', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory() },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      await screen.findByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(api.patchOffer).toHaveBeenCalled()
    expect(api.postPriceCategories).toHaveBeenCalled()
  })

  it('should notify an error when submit fail', async () => {
    jest.spyOn(api, 'postPriceCategories').mockRejectedValue({})

    renderPriceCategories(
      { offer: individualOfferFactory() },
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Prix par personne'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      await screen.findByText(
        'Une erreur est survenue lors de la mise à jour de votre tarif'
      )
    ).toBeInTheDocument()
  })
})
