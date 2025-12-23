import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  ShareTemplateOfferLink,
  type ShareTemplateOfferLinkProps,
} from './ShareTemplateOfferLink'

const renderShareTemplateOfferLink = ({
  offerId,
  notifySuccessMessage,
}: ShareTemplateOfferLinkProps) =>
  renderWithProviders(
    <>
      <ShareTemplateOfferLink
        offerId={offerId}
        notifySuccessMessage={notifySuccessMessage}
      />
      <SnackBarContainer />
    </>
  )

describe('ShareTemplateOfferLink', () => {
  const offerId = 1234
  const notifySuccessMessage = 'Le lien ADAGE a bien été copié'
  const fullLink = `https://bv.ac-versailles.fr/adage/passculture/offres/offerid/${offerId}/source/shareLink`

  it('should render the ShareLink input with the correct value', () => {
    renderShareTemplateOfferLink({ offerId, notifySuccessMessage })
    const input = screen.getByLabelText(/Lien de l’offre/i)
    expect(input).toHaveValue(fullLink)
  })

  it('should render the copy button', () => {
    renderShareTemplateOfferLink({ offerId, notifySuccessMessage })
    const button = screen.getByRole('button', { name: /Copier/i })
    expect(button).toBeInTheDocument()
  })

  it('should show the info callout', () => {
    renderShareTemplateOfferLink({ offerId, notifySuccessMessage })
    expect(
      screen.getByText(
        /Veillez à préciser aux enseignants de se connecter à ADAGE avant d’ouvrir ce lien de partage sans quoi ils n’y auront pas accès./i
      )
    ).toBeInTheDocument()
  })
})
