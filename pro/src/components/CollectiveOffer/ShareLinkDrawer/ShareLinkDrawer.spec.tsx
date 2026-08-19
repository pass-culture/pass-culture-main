import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ShareLinkDrawer } from './ShareLinkDrawer'

vi.mock('../ShareTemplateOfferLink/ShareTemplateOfferLink', () => ({
  ShareTemplateOfferLink: () => <div>ShareTemplateOfferLink</div>,
}))

describe('ShareLinkDrawer', () => {
  describe('uncontrolled mode', () => {
    it('should open the modal on trigger button click', async () => {
      renderWithProviders(<ShareLinkDrawer offerId={1} />)

      expect(
        screen.queryByRole('heading', {
          name: /Aidez les enseignants/i,
        })
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: /Partager l’offre/i })
      )

      expect(
        screen.getByRole('heading', {
          name: /Aidez les enseignants/i,
        })
      ).toBeInTheDocument()
    })

    it('should close the modal on "Fermer" click', async () => {
      renderWithProviders(<ShareLinkDrawer offerId={1} />)

      await userEvent.click(
        screen.getByRole('button', { name: /Partager l’offre/i })
      )

      expect(
        screen.getByRole('heading', { name: /Aidez les enseignants/i })
      ).toBeInTheDocument()

      await userEvent.click(screen.getByRole('button', { name: 'Fermer' }))

      expect(
        screen.queryByRole('heading', { name: /Aidez les enseignants/i })
      ).not.toBeInTheDocument()
    })
  })
})
