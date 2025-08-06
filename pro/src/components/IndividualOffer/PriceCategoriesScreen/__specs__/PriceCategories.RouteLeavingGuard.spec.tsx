import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { generatePath, Route, Routes } from 'react-router'

import { api } from '@/apiClient//api'
import {
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from '@/apiClient//v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'

import {
  PriceCategoriesScreen,
  PriceCategoriesScreenProps,
} from '../PriceCategoriesScreen'

const renderPriceCategories = ({
  props,
  url = generatePath(
    getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
      mode: OFFER_WIZARD_MODE.CREATION,
    }),
    { offerId: 'AA' }
  ),
  features = [],
}: {
  props: PriceCategoriesScreenProps
  url?: string
  features?: string[]
}) =>
  renderWithProviders(
    <Routes>
      {[OFFER_WIZARD_MODE.CREATION, OFFER_WIZARD_MODE.EDITION].map((mode) => (
        <Route
          key={mode}
          path={getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
            mode,
          })}
          element={
            <>
              <PriceCategoriesScreen {...props} />
              <ButtonLink to="/outside">Go outside !</ButtonLink>
              <ButtonLink
                to={getIndividualOfferPath({
                  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
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
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>There is the informations route content</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>There is the media route content</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>There is the stock create route content</div>}
      />

      <Route
        path={getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
        })}
        element={<div>This is the summary route content</div>}
      />
    </Routes>,
    { initialRouterEntries: [url], features }
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

  describe('when video is enabled', () => {
    it('should let going to media when clicking on previous step in creation', async () => {
      renderPriceCategories({
        props: { offer: getIndividualOfferFactory() },
        features: ['WIP_ADD_VIDEO'],
      })

      await userEvent.click(screen.getByText('Retour'))

      expect(
        screen.getByText('There is the media route content')
      ).toBeInTheDocument()
    })
  })

  it('should let going to information when clicking on previous step in creation', async () => {
    renderPriceCategories({
      props: { offer: getIndividualOfferFactory() },
    })

    await userEvent.click(screen.getByText('Retour'))

    expect(
      screen.getByText('There is the informations route content')
    ).toBeInTheDocument()
  })

  it('should let going to stock when form has been filled in creation', async () => {
    renderPriceCategories({ props: { offer: getIndividualOfferFactory() } })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    await waitFor(() => {
      expect(
        screen.getByText('There is the stock create route content')
      ).toBeInTheDocument()
    })
  })

  it('should let going to recap when form has been filled in edition', async () => {
    renderPriceCategories({
      props: { offer: getIndividualOfferFactory() },
      url: generatePath(
        getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      ),
    })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      screen.getByText('This is the summary route content')
    ).toBeInTheDocument()
  })

  it('should go back to summary when clicking on "Annuler et quitter" in Edition', async () => {
    renderPriceCategories({
      props: { offer: getIndividualOfferFactory() },
      url: generatePath(
        getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      ),
    })

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('This is the summary route content')
    ).toBeInTheDocument()
  })
})
