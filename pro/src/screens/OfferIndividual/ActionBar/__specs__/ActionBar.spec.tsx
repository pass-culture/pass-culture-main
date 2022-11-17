import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { configureTestStore } from 'store/testUtils'

import { ActionBar } from '..'
import { IActionBarProps } from '../ActionBar'

const renderActionBar = ({
  props,
  url = '/creation/testUrl',
}: {
  props: IActionBarProps
  url?: string
}) => {
  return render(
    <Provider
      store={configureTestStore({
        offers: {
          searchFilters: {
            filter: 'my_filter',
            other_filter: 'my_other_filter',
          },
          pageNumber: 3,
        },
      })}
    >
      <MemoryRouter initialEntries={[url]}>
        <ActionBar {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('OfferIndividual::ActionBar', () => {
  let props: IActionBarProps
  const onClickPreviousMock = jest.fn()
  const onClickNextMock = jest.fn()
  const onClickSaveDraftMock = jest.fn()

  beforeEach(() => {
    props = {
      onClickPrevious: onClickPreviousMock,
      onClickNext: onClickNextMock,
      onClickSaveDraft: onClickSaveDraftMock,
      step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      isDisabled: false,
    }
  })

  describe('on creation', () => {
    it('should render the component for information page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.INFORMATIONS

      renderActionBar({ props })

      const buttonCancel = screen.getByText('Annuler et quitter')
      expect(buttonCancel).toHaveAttribute('href', '/offres')
      const buttonSaveDraft = screen.getByText('Sauvegarder le brouillon')
      await userEvent.click(buttonSaveDraft)
      expect(onClickSaveDraftMock).toHaveBeenCalled()
      const buttonNextStep = screen.getByText('Étape suivante')
      await userEvent.click(buttonNextStep)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for stock page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.STOCKS

      renderActionBar({ props })

      const buttonPreviousStep = screen.getByText('Étape précédente')
      await userEvent.click(buttonPreviousStep)
      expect(onClickPreviousMock).toHaveBeenCalled()
      const buttonSaveDraft = screen.getByText('Sauvegarder le brouillon')
      await userEvent.click(buttonSaveDraft)
      expect(onClickSaveDraftMock).toHaveBeenCalled()
      const buttonNextStep = screen.getByText('Étape suivante')
      await userEvent.click(buttonNextStep)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for summary page', async () => {
      props.step = OFFER_WIZARD_STEP_IDS.SUMMARY

      renderActionBar({ props })

      const buttonPreviousStep = screen.getByText('Étape précédente')
      await userEvent.click(buttonPreviousStep)
      expect(onClickPreviousMock).toHaveBeenCalled()
      const buttonSaveDraft = screen.getByText(
        'Sauvegarder le brouillon et quitter'
      )
      expect(buttonSaveDraft).toHaveAttribute('href', '/offres')
      const buttonPublishOffer = screen.getByText("Publier l'offre")
      await userEvent.click(buttonPublishOffer)
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
        '/offres?filter=my_filter&other_filter=my_other_filter&page=3'
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
        '/offres?filter=my_filter&other_filter=my_other_filter&page=3'
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
        '/offres?filter=my_filter&other_filter=my_other_filter&page=3'
      )
    })
  })
})
