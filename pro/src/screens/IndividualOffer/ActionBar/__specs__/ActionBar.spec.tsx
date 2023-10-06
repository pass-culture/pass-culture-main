import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import ActionBar, { ActionBarProps } from '../ActionBar'

const renderActionBar = ({
  props,
  url = '/creation/testUrl',
}: {
  props: ActionBarProps
  url?: string
}) => {
  const storeOverrides = {
    offers: {
      searchFilters: {
        filter: 'my_filter',
        other_filter: 'my_other_filter',
      },
      pageNumber: 3,
    },
  }

  return renderWithProviders(<ActionBar {...props} />, {
    storeOverrides,
    initialRouterEntries: [url],
  })
}

describe('IndividualOffer::ActionBar', () => {
  let props: ActionBarProps
  const onClickPreviousMock = vi.fn()
  const onClickNextMock = vi.fn()

  beforeEach(() => {
    props = {
      onClickPrevious: onClickPreviousMock,
      onClickNext: onClickNextMock,
      step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      isDisabled: false,
    }
  })

  describe('on creation', () => {
    it('should render the component for information page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.INFORMATIONS

      renderActionBar({ props })

      expect(screen.getByText('Retour')).toBeInTheDocument()
      const buttonNextStep = screen.getByText('Enregistrer et continuer')
      await userEvent.click(buttonNextStep)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for stock page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.STOCKS

      renderActionBar({ props })

      const buttonPreviousStep = screen.getByText('Retour')
      await userEvent.click(buttonPreviousStep)
      expect(onClickPreviousMock).toHaveBeenCalled()
      const buttonNextStep = screen.getByText('Enregistrer et continuer')
      await userEvent.click(buttonNextStep)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for summary page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.SUMMARY

      renderActionBar({ props })

      const buttonPreviousStep = screen.getByText('Retour')
      await userEvent.click(buttonPreviousStep)
      expect(onClickPreviousMock).toHaveBeenCalled()
      const buttonSaveDraft = screen.getByText(
        'Sauvegarder le brouillon et quitter'
      )
      expect(buttonSaveDraft).toHaveAttribute('href', '/offres')
      const buttonPublishOffer = screen.getByText('Publier l’offre')
      await userEvent.click(buttonPublishOffer)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should show draft saved indicator', async () => {
      props.dirtyForm = false

      renderActionBar({ props })
      expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()
      expect(
        screen.queryByText('Brouillon non enregistré')
      ).not.toBeInTheDocument()
    })

    it('should show draft not saved indicator', async () => {
      props.dirtyForm = true

      renderActionBar({ props })
      expect(screen.queryByText('Brouillon enregistré')).not.toBeInTheDocument()
      expect(screen.getByText('Brouillon non enregistré')).toBeInTheDocument()
    })
  })

  describe('on draft', () => {
    it('should render the component for information page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.INFORMATIONS

      renderActionBar({ props, url: '/brouillon/url' })

      expect(screen.getByText('Annuler et quitter')).toBeInTheDocument()
      const buttonNextStep = screen.getByText('Enregistrer et continuer')
      await userEvent.click(buttonNextStep)
      expect(onClickNextMock).toHaveBeenCalled()
    })
  })

  describe('on edition', () => {
    it('should render the component for information page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.INFORMATIONS

      renderActionBar({ props, url: '/edition/url' })

      const buttonCancel = screen.getByText('Annuler et quitter')
      expect(buttonCancel).toHaveAttribute(
        'href',
        '/offres?page=3&filter=my_filter&other_filter=my_other_filter'
      )
      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for stock page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.STOCKS

      renderActionBar({ props, url: '/edition/url' })

      const buttonCancel = screen.getByText('Annuler et quitter')
      expect(buttonCancel).toHaveAttribute(
        'href',
        '/offres?page=3&filter=my_filter&other_filter=my_other_filter'
      )
      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for summary page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.SUMMARY

      renderActionBar({ props, url: '/edition/url' })

      const buttonBack = screen.getByText('Retour à la liste des offres')
      expect(buttonBack).toHaveAttribute(
        'href',
        '/offres?page=3&filter=my_filter&other_filter=my_other_filter'
      )
    })
  })
})
