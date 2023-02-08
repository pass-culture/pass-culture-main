import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath } from 'react-router'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const mockLogEvent = jest.fn()

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
            element={
              <>
                <PriceCategories {...props} />
                <ButtonLink link={{ to: '/outside', isExternal: false }}>
                  Go outside !
                </ButtonLink>
              </>
            }
            key={mode}
          />
        ))}
      </Routes>
    </>,
    { initialRouterEntries: [url] }
  )

describe('trackers for PriceCategories', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest
      .spyOn(api, 'postPriceCategories')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should track when clicking on Etape suivante in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: 'stocks',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on Etape précédente in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on Sauvegarder le brouillon in creation', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })
    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: 'tarifs',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on Etape suivante in draft', async () => {
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

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: true,
        offerId: 'AA',
        to: 'stocks',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on Etape précédente in draft', async () => {
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

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: true,
        offerId: 'AA',
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on Sauvegarder le brouillon in draft', async () => {
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

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: true,
        offerId: 'AA',
        to: 'tarifs',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on Enregistrer les modifications in edition', async () => {
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

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: false,
        isEdition: true,
        offerId: 'AA',
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on Annuler et quitter in edition', async () => {
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
    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: false,
        isEdition: true,
        offerId: 'AA',
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking from routeLeavingGuard', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })

    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Étape précédente'))

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: 'informations',
        used: 'RouteLeavingGuard',
      }
    )
  })

  it('should track when clicking from routeLeavingGuard and going outside', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })

    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: '/outside',
        used: 'RouteLeavingGuard',
      }
    )
  })

  it('should track when clicking from routeLeavingGuard but cancelling', async () => {
    renderPriceCategories({ offer: individualOfferFactory({ id: 'AA' }) })

    await userEvent.type(
      screen.getByLabelText('Intitulé du tarif'),
      'Mon tarif'
    )
    await userEvent.type(screen.getByLabelText('Tarif par personne'), '20')

    await userEvent.click(screen.getByText('Étape précédente'))

    await userEvent.click(screen.getByText('Ne pas enregistrer'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'tarifs',
        isDraft: true,
        isEdition: false,
        offerId: 'AA',
        to: 'informations',
        used: 'RouteLeavingGuard',
      }
    )
  })
})
