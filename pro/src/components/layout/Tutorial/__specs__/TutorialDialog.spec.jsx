import '@testing-library/jest-dom'

import { act, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import TutorialDialogContainer from 'components/layout/Tutorial/TutorialDialogContainer'
import { Events } from 'core/FirebaseEvents/constants'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

jest.mock('repository/pcapi/pcapi', () => ({
  setHasSeenTutos: jest.fn().mockResolvedValue({}),
}))

const stepTitles = [
  'Bienvenue dans l’espace acteurs culturels',
  'Gérer vos lieux culturels',
  'Créer une offre',
  'Suivre et gérer vos réservations',
]

const renderTutorialDialog = async (store, props = {}) => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <TutorialDialogContainer {...props} />
      </MemoryRouter>
    </Provider>
  )
}

const mockLogEvent = jest.fn()

describe('tutorial modal', () => {
  let store

  beforeEach(() => {
    store = configureTestStore({})
  })
  it('should trigger an event when the user arrive on /accueil for the first time', async () => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    store = configureTestStore({
      user: {
        currentUser: {
          id: 'test_id',
          hasSeenProTutorials: false,
        },
      },
    })
    renderTutorialDialog(store, {})
    const closeButton = screen.getByTitle('Fermer la modale')
    await userEvent.click(closeButton)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.TUTO_PAGE_VIEW, {
      page_number: '1',
    })
    expect(mockLogEvent).toHaveBeenNthCalledWith(2, Events.FIRST_LOGIN)
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
  })

  it('should show tutorial dialog if user has not seen it yet', async () => {
    store = configureTestStore({
      user: {
        currentUser: {
          id: 'test_id',
          hasSeenProTutorials: false,
        },
      },
    })

    const props = {}
    await renderTutorialDialog(store, props)

    expect(screen.getByText(stepTitles[0])).toBeInTheDocument()
  })

  it("shouldn't show tutorial dialog if user has already seen it", async () => {
    store = configureTestStore({
      user: {
        currentUser: {
          id: 'test_id',
          hasSeenProTutorials: true,
        },
      },
    })
    const props = {}

    await renderTutorialDialog(store, props)

    expect(screen.queryByText(stepTitles[0])).not.toBeInTheDocument()
  })

  describe('interacting with navigation buttons', () => {
    let buttonNext
    beforeEach(async () => {
      store = configureTestStore({
        user: {
          currentUser: {
            id: 'test_id',
            hasSeenProTutorials: false,
          },
        },
      })

      await renderTutorialDialog(store)
      buttonNext = screen.getByText('Suivant')
    })

    describe('from first step', () => {
      it('should disabled "previous" button', async () => {
        const buttonPrevious = screen.getByText('Précédent')
        expect(buttonPrevious).toHaveAttribute('disabled')
      })

      it('should show change steps when clicking on "next"', async () => {
        expect(screen.getByText(stepTitles[0])).toBeInTheDocument()

        await fireEvent.click(buttonNext)
        expect(screen.getByText(stepTitles[1])).toBeInTheDocument()

        await fireEvent.click(buttonNext)
        expect(screen.getByText(stepTitles[2])).toBeInTheDocument()

        await fireEvent.click(buttonNext)
        expect(screen.getByText(stepTitles[3])).toBeInTheDocument()
      })
    })

    describe('from last step', () => {
      let buttonPrevious

      beforeEach(async () => {
        await fireEvent.click(buttonNext)
        await fireEvent.click(buttonNext)
        await fireEvent.click(buttonNext)

        buttonPrevious = screen.getByText('Précédent')
      })

      describe('when clicking on finish button', () => {
        it('should close tutorial', async () => {
          const buttonFinish = screen.queryByText('Terminer')
          expect(buttonFinish).toBeInTheDocument()

          expect(screen.getByTestId('tutorial-container')).toBeInTheDocument()
          await act(async () => {
            await fireEvent.click(buttonFinish)
          })
          expect(
            screen.queryByTestId('tutorial-container')
          ).not.toBeInTheDocument()
        })

        it('should call set has seen tutos function', async () => {
          const buttonFinish = screen.queryByText('Terminer')
          expect(buttonFinish).toBeInTheDocument()

          expect(screen.getByTestId('tutorial-container')).toBeInTheDocument()
          await act(async () => {
            await fireEvent.click(buttonFinish)
          })
          expect(pcapi.setHasSeenTutos).toHaveBeenCalledWith()
        })
      })

      it('should change step when clicking on "next"', async () => {
        expect(screen.getByText(stepTitles[3])).toBeInTheDocument()

        await fireEvent.click(buttonPrevious)
        expect(screen.getByText(stepTitles[2])).toBeInTheDocument()

        await fireEvent.click(buttonPrevious)
        expect(screen.getByText(stepTitles[1])).toBeInTheDocument()

        await fireEvent.click(buttonPrevious)
        expect(screen.getByText(stepTitles[0])).toBeInTheDocument()
      })
    })

    it('should change step when clicking on "previous"', async () => {
      await fireEvent.click(buttonNext)
      await fireEvent.click(buttonNext)
      await fireEvent.click(buttonNext)

      const buttonPrevious = screen.queryByText('Précédent')

      expect(screen.getByText(stepTitles[3])).toBeInTheDocument()

      await fireEvent.click(buttonPrevious)
      expect(screen.getByText(stepTitles[2])).toBeInTheDocument()

      await fireEvent.click(buttonPrevious)
      expect(screen.getByText(stepTitles[1])).toBeInTheDocument()

      await fireEvent.click(buttonPrevious)
      expect(screen.getByText(stepTitles[0])).toBeInTheDocument()
    })

    it('should go on the right step when clicking on dots', async () => {
      const navDottes = screen.queryAllByTestId('nav-dot')

      expect(screen.getByText(stepTitles[0])).toBeInTheDocument()

      await fireEvent.click(navDottes[3])
      expect(screen.getByText(stepTitles[3])).toBeInTheDocument()

      await fireEvent.click(navDottes[1])
      expect(screen.getByText(stepTitles[1])).toBeInTheDocument()

      await fireEvent.click(navDottes[0])
      expect(screen.getByText(stepTitles[0])).toBeInTheDocument()

      await fireEvent.click(navDottes[2])
      expect(screen.getByText(stepTitles[2])).toBeInTheDocument()
    })
  })
})
