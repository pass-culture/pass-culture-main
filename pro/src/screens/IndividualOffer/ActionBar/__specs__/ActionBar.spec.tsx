import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ActionBar, ActionBarProps } from '../ActionBar'

const renderActionBar = ({
  props,
  url = '/creation/testUrl',
}: {
  props: ActionBarProps
  url?: string
}) => {
  return renderWithProviders(<ActionBar {...props} />, {
    storeOverrides: {},
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
      expect(screen.getByText('Publier l’offre')).toBeInTheDocument()
    })

    it('should show draft saved indicator', () => {
      props.dirtyForm = false

      renderActionBar({ props })
      expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()
      expect(
        screen.queryByText('Brouillon non enregistré')
      ).not.toBeInTheDocument()
    })

    it('should show draft not saved indicator', () => {
      props.dirtyForm = true

      renderActionBar({ props })
      expect(screen.queryByText('Brouillon enregistré')).not.toBeInTheDocument()
      expect(screen.getByText('Brouillon non enregistré')).toBeInTheDocument()
    })
  })

  describe('on edition', () => {
    it('should render the component for information page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.INFORMATIONS

      renderActionBar({ props, url: '/edition/url' })

      await userEvent.click(screen.getByText('Annuler et quitter'))
      expect(onClickPreviousMock).toHaveBeenCalled()

      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for stock page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.STOCKS

      renderActionBar({ props, url: '/edition/url' })

      await userEvent.click(screen.getByText('Annuler et quitter'))
      expect(onClickPreviousMock).toHaveBeenCalled()

      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for summary page', () => {
      props.step = OFFER_WIZARD_STEP_IDS.SUMMARY

      renderActionBar({ props, url: '/edition/url' })

      const buttonBack = screen.getByText('Retour à la liste des offres')
      expect(buttonBack).toHaveAttribute('href', '/offres')
    })
  })
})
