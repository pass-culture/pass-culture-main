import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

export const getContactInputs = async () => {
  const contactTitle = await screen.findByText('Contact')
  const contactNode = contactTitle.parentNode.parentNode

  const contactPhoneNumber = await screen.findByLabelText('Téléphone :')
  const contactMail = await within(contactNode).findByLabelText('Mail :')
  const contactUrl = await screen.findByLabelText('URL de votre site web :')

  const clearAndFillContact = ({ phoneNumber, email, website }) => {
    userEvent.clear(contactPhoneNumber)
    userEvent.clear(contactMail)
    userEvent.clear(contactUrl)

    userEvent.paste(contactPhoneNumber, phoneNumber)
    userEvent.paste(contactMail, email)
    userEvent.paste(contactUrl, website)
  }

  return {
    contactPhoneNumber,
    contactMail,
    contactUrl,
    clearAndFillContact,
  }
}
