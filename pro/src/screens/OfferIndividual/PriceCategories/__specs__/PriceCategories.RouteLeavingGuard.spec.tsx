import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route } from 'react-router'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { ButtonLink } from 'ui-kit'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const mockHistoryPush = jest.fn()
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

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
      <Route
        path={Object.values(OFFER_WIZARD_MODE).map(mode =>
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.TARIFS,
            mode,
          })
        )}
      >
        <PriceCategories {...props} />
        <ButtonLink link={{ to: '/outside', isExternal: false }}>
          Go outside !
        </ButtonLink>
        <ButtonLink
          link={{
            to: getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode: OFFER_WIZARD_MODE.DRAFT,
            }),
            isExternal: false,
          }}
        >
          Go to stocks !
        </ButtonLink>
      </Route>
      <Route path="/outside">
        <div>This is outside offer creation</div>
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        })}
      >
        <div>There is the stock route content</div>
      </Route>
    </>,
    { initialRouterEntries: [url] }
  )

describe('PriceCategories', () => {
  it('should let going to information when clicking on previous step in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockHistoryPush).toHaveBeenCalledWith(
      '/offre/individuelle/AA/creation/informations'
    )
  })

  it('should let going to stock when form has been filled in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockHistoryPush).toHaveBeenCalledWith(
      '/offre/individuelle/AA/creation/stocks'
    )
  })

  it('should let going to stock when form has been filled in draft', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory({ id: 'AA' }) },

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
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockHistoryPush).toHaveBeenCalledWith(
      '/offre/individuelle/AA/brouillon/stocks'
    )
  })

  it('should stay on the same page when clicking on "Sauvegarder le brouillon" in draft', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory({ id: 'AA' }) },
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
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockHistoryPush).toHaveBeenCalledWith(
      '/offre/individuelle/AA/brouillon/tarifs'
    )
  })

  it('should let going to recap when form has been filled in edition', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory({ id: 'AA' }) },
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
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(mockHistoryPush).toHaveBeenCalledWith(
      '/offre/individuelle/AA/recapitulatif'
    )
  })

  it('should let going to outside when form has been filled in draft and clicking from leaving guard', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory({ id: 'AA' }) },
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
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Go outside !'))
    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      screen.getByText('This is outside offer creation')
    ).toBeInTheDocument()
  })

  it('should let going to internal navigation when form has been filled in draft and clicking from leaving guard', async () => {
    renderPriceCategories(
      { offer: individualOfferFactory({ id: 'AA' }) },
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
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Go to stocks !'))
    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(
      screen.getByText('There is the stock route content')
    ).toBeInTheDocument()
  })
})
