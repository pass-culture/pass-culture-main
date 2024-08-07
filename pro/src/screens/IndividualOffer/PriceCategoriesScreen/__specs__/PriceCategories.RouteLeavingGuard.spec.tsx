import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'
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
    <Routes>
      {[OFFER_WIZARD_MODE.CREATION, OFFER_WIZARD_MODE.EDITION].map((mode) => (
        <Route
          key={mode}
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.TARIFS,
            mode,
          })}
          element={
            <>
              <PriceCategoriesScreen {...props} />
              <ButtonLink to="/outside">Go outside !</ButtonLink>
              <ButtonLink
                to={getIndividualOfferPath({
                  step: OFFER_WIZARD_STEP_IDS.STOCKS,
                  mode: OFFER_WIZARD_MODE.CREATION,
                })}
              >
                Go to stocks !
              </ButtonLink>
            </>
          }
        />
      ))}
      <Route
        path="/outside"
        element={<div>This is outside offer creation</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>There is the informations route content</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>There is the stock create route content</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
        })}
        element={<div>This is the summary route content</div>}
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )

describe('PriceCategories', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferWithAddressResponseModel
    )
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'postPriceCategories').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should let going to information when clicking on previous step in creation', async () => {
    renderPriceCategories({ offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByText('Retour'))

    expect(
      screen.getByText('There is the informations route content')
    ).toBeInTheDocument()
  })

  it('should let going to stock when form has been filled in creation', async () => {
    renderPriceCategories({ offer: getIndividualOfferFactory() })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif *'),
      'Mon tarif'
    )

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      screen.getByText('There is the stock create route content')
    ).toBeInTheDocument()
  })

  it('should let going to recap when form has been filled in edition', async () => {
    renderPriceCategories(
      { offer: getIndividualOfferFactory() },
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

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      screen.getByText('This is the summary route content')
    ).toBeInTheDocument()
  })

  it('should go back to summary when clicking on "Annuler et quitter" in Edition', async () => {
    renderPriceCategories(
      { offer: getIndividualOfferFactory() },
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      )
    )

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('This is the summary route content')
    ).toBeInTheDocument()
  })
})
