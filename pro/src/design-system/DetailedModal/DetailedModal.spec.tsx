import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, vi } from 'vitest'
import { axe } from 'vitest-axe'
import '@testing-library/jest-dom/vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { DetailedModalProps } from './DetailedModal'
import { DetailedModal } from './DetailedModal'

const defaultProps: DetailedModalProps = {
  isOpen: true,
  onClose: vi.fn(),
  title: 'Titre de la modale',
  children: <p>Contenu de la modale</p>,
}

function renderDetailedModal(props?: Partial<DetailedModalProps>) {
  return renderWithProviders(<DetailedModal {...defaultProps} {...props} />)
}

describe('DetailedModal', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderDetailedModal()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the title and children when open', () => {
    renderDetailedModal()

    expect(
      screen.getByRole('heading', { name: 'Titre de la modale' })
    ).toBeVisible()
    expect(screen.getByText('Contenu de la modale')).toBeVisible()
  })

  it('should not have the open attribute when isOpen is false', () => {
    renderDetailedModal({ isOpen: false })

    expect(screen.getByRole('dialog', { hidden: true })).not.toHaveAttribute(
      'open'
    )
  })

  it('should call onClose when the close button is clicked', async () => {
    const onClose = vi.fn()
    renderDetailedModal({ onClose })

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la boite de dialogue' })
    )

    expect(onClose).toHaveBeenCalledOnce()
  })

  it('should focus the close button when opening', async () => {
    renderDetailedModal()

    const closeButton = screen.getByRole('button', {
      name: 'Fermer la boite de dialogue',
    })

    await waitFor(() => {
      expect(closeButton).toHaveFocus()
    })
  })

  it('should move focus from close button to go back button on Tab', async () => {
    const user = userEvent.setup()
    renderDetailedModal({ onGoBack: vi.fn() })

    const closeButton = screen.getByRole('button', {
      name: 'Fermer la boite de dialogue',
    })
    const goBackButton = screen.getByRole('button', {
      name: 'Retourner à l\u2019étape précédente',
    })

    await waitFor(() => {
      expect(closeButton).toHaveFocus()
    })

    await user.tab()

    expect(goBackButton).toHaveFocus()
  })

  describe('go back button', () => {
    it('should not display the go back button when onGoBack is not provided', () => {
      renderDetailedModal()

      expect(
        screen.queryByRole('button', {
          name: 'Retourner à l’étape précédente',
        })
      ).not.toBeInTheDocument()
    })

    it('should display the go back button when onGoBack is provided', () => {
      renderDetailedModal({ onGoBack: vi.fn() })

      expect(
        screen.getByRole('button', {
          name: 'Retourner à l\u2019étape précédente',
        })
      ).toBeVisible()
    })

    it('should call onGoBack when the go back button is clicked', async () => {
      const onGoBack = vi.fn()
      renderDetailedModal({ onGoBack })

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Retourner à l\u2019étape précédente',
        })
      )

      expect(onGoBack).toHaveBeenCalledOnce()
    })

    it('should use a custom aria-label for the go back button when provided', () => {
      renderDetailedModal({
        onGoBack: vi.fn(),
        goBackButtonAriaLabel: 'Retour',
      })

      expect(screen.getByRole('button', { name: 'Retour' })).toBeVisible()
    })
  })

  describe('description', () => {
    it('should not display description when not provided', () => {
      renderDetailedModal()

      expect(
        screen.queryByText('Description de la modale')
      ).not.toBeInTheDocument()
    })

    it('should display description when provided', () => {
      renderDetailedModal({ description: 'Description de la modale' })

      expect(screen.getByText('Description de la modale')).toBeVisible()
    })
  })

  describe('footer actions', () => {
    it('should not display the footer when no actions are provided', () => {
      renderDetailedModal()

      expect(screen.queryByRole('contentinfo')).not.toBeInTheDocument()
    })

    it('should display primary action when provided', () => {
      renderDetailedModal({ primaryAction: <button>Valider</button> })

      expect(screen.getByRole('button', { name: 'Valider' })).toBeVisible()
    })

    it('should display all actions when provided', () => {
      renderDetailedModal({
        primaryAction: <button>Valider</button>,
        secondaryAction: <button>Annuler</button>,
        tertiaryAction: <button>Tertiaire</button>,
      })

      expect(screen.getByRole('button', { name: 'Valider' })).toBeVisible()
      expect(screen.getByRole('button', { name: 'Annuler' })).toBeVisible()
      expect(screen.getByRole('button', { name: 'Tertiaire' })).toBeVisible()
    })

    it('should display the footer message when provided', () => {
      renderDetailedModal({
        primaryAction: <button>Valider</button>,
        footerMessage: 'Message de pied de page',
      })

      expect(screen.getByText('Message de pied de page')).toBeVisible()
    })

    it('should not display footer when loadingState is active', () => {
      renderDetailedModal({
        loadingState: { label: 'Chargement en cours...' },
        primaryAction: <button>Valider</button>,
      })

      expect(screen.queryByRole('contentinfo')).not.toBeInTheDocument()
    })
  })

  describe('loading state', () => {
    it('should display loading label when loadingState is provided', () => {
      renderDetailedModal({ loadingState: { label: 'Chargement en cours...' } })

      expect(screen.getByText('Chargement en cours...')).toBeVisible()
    })

    it('should not display children when loadingState is provided', () => {
      renderDetailedModal({ loadingState: { label: 'Chargement en cours...' } })

      expect(screen.queryByText('Contenu de la modale')).not.toBeInTheDocument()
    })
  })
})
