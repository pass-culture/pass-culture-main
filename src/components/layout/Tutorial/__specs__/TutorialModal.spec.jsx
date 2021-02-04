import '@testing-library/jest-dom'
import { act, fireEvent, render, screen } from '@testing-library/react'
import React, { Fragment } from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import Modal from 'components/layout/Modal'
import { configureTestStore } from 'store/testUtils'

import TutorialModalContainer from '../TutorialModalContainer'

const stepTitles = [
  "Bienvenue dans l'espace acteurs culturels",
  'Gérer vos lieux culturels',
  'Créer une offre',
  'Suivre et gérer vos réservations',
]

const renderTutorialModal = async (store, props = {}) => {
  return await act(async () => {
    return render(
      <Provider store={store}>
        <MemoryRouter>
          <Fragment>
            <TutorialModalContainer {...props} />
            <Modal key="modal" />
          </Fragment>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('tutorialModal', () => {
  let store

  beforeEach(() => {
    store = configureTestStore({})
  })

  it('should show tutorial modal if user has not seen it yet', async () => {
    store = configureTestStore({
      data: {
        features: [
          {
            id: 'Test_id',
            description: 'Dummy description',
            isActive: true,
            name: 'Dummy name',
            nameKey: 'PRO_TUTO',
          },
        ],
        users: [
          {
            id: 'test_id',
            hasSeenTutorial: false,
          },
        ],
      },
    })

    const props = {}
    await renderTutorialModal(store, props)

    expect(screen.getByText(stepTitles[0])).toBeInTheDocument()
  })

  it("shouldn't show tutorial modal if user has already seen it", async () => {
    store = configureTestStore({
      data: {
        features: [
          {
            id: 'Test_id',
            description: 'Dummy description',
            isActive: true,
            name: 'Dummy name',
            nameKey: 'PRO_TUTO',
          },
        ],
        users: [
          {
            id: 'test_id',
            hasSeenTutorial: true,
          },
        ],
      },
    })
    const props = {}

    await renderTutorialModal(store, props)

    expect(screen.queryByText(stepTitles[0])).not.toBeInTheDocument()
  })

  describe('interacting with navigation buttons', () => {
    let buttonNext
    beforeEach(async () => {
      store = configureTestStore({
        data: {
          features: [
            {
              id: 'Test_id',
              description: 'Dummy description',
              isActive: true,
              name: 'Dummy name',
              nameKey: 'PRO_TUTO',
            },
          ],
          users: [
            {
              id: 'test_id',
              hasSeenTutorial: false,
            },
          ],
        },
      })

      await renderTutorialModal(store)
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

      it('should close tutoral on click on "finish" button', async () => {
        const buttonFinish = screen.queryByText('Terminer')
        expect(buttonFinish).toBeInTheDocument()

        expect(screen.getByTestId('tutorial-container')).toBeInTheDocument()
        await fireEvent.click(buttonFinish)
        expect(screen.queryByTestId('tutorial-container')).not.toBeInTheDocument()
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
