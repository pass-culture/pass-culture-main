import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ActionBar, type ActionBarProps } from './ActionBar'

const renderActionBar = ({
  props,
  url = '/creation/testUrl',
  features = [],
}: {
  props: ActionBarProps
  url?: string
  features?: string[]
}) => {
  return renderWithProviders(<ActionBar {...props} />, {
    features: features,
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
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
      isDisabled: false,
    }
  })

  describe('on creation', () => {
    it('should always display a "Retour" button', async () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
      renderActionBar({ props })

      const previousStepButton = screen.getByText(/Retour/)
      await userEvent.click(previousStepButton)
      expect(onClickPreviousMock).toHaveBeenCalled()
    })

    it('should display "Sauvegarder le brouillon" and "Publier l’offre" buttons on summary page', () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY
      renderActionBar({ props })

      const saveDraftButton = screen.getByRole('link', {
        name: /Sauvegarder le brouillon/,
      })
      expect(saveDraftButton).toHaveAttribute('href', '/offres')

      const submitButton = screen.getByRole('button', {
        name: 'Publier l’offre',
      })
      expect(submitButton).toHaveAttribute('type', 'submit')
    })

    it('should display "Enregistrer et continuer" button on other pages', () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION
      renderActionBar({ props })

      const submitButton = screen.getByRole('button', {
        name: /Enregistrer et continuer/,
      })
      expect(submitButton).toHaveAttribute('type', 'submit')
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
    it('should render the component for details page', async () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION

      renderActionBar({ props, url: '/edition/url' })

      await userEvent.click(screen.getByText('Annuler et quitter'))
      expect(onClickPreviousMock).toHaveBeenCalled()

      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for tarifs page', async () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
      props.isEvent = false

      renderActionBar({ props, url: '/edition/url' })

      await userEvent.click(screen.getByText('Annuler et quitter'))
      expect(onClickPreviousMock).toHaveBeenCalled()

      const buttonSave = screen.getByText('Enregistrer les modifications')
      await userEvent.click(buttonSave)
      expect(onClickNextMock).toHaveBeenCalled()
    })

    it('should render the component for summary page', () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY

      renderActionBar({ props, url: '/edition/url' })

      const buttonBack = screen.getByRole('link', {
        name: 'Retour à la liste des offres',
      })
      expect(buttonBack).toHaveAttribute('href', '/offres')
    })

    it('should show a button to go back read only when editing stocks (timetable)', async () => {
      props.step = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
      props.isEvent = true

      renderActionBar({
        props,
        url: '/edition/url',
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Quitter le mode édition' })
      )

      expect(onClickPreviousMock).toHaveBeenCalled()
    })
  })
})
