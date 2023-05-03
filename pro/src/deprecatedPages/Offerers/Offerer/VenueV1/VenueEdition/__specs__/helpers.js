import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

export const getContactInputs = async () => {
  const contactTitle = await screen.findByText('Contact')
  const contactNode = contactTitle.parentNode.parentNode

  const contactPhoneNumber = await screen.findByLabelText('Téléphone :')
  const contactMail = await within(contactNode).findByLabelText('Mail :')
  const contactUrl = await screen.findByLabelText('URL de votre site web :')

  const clearAndFillContact = async ({ phoneNumber, email, website }) => {
    await userEvent.clear(contactPhoneNumber)
    await userEvent.clear(contactMail)
    await userEvent.clear(contactUrl)

    await userEvent.type(contactPhoneNumber, phoneNumber)
    await userEvent.type(contactMail, email)
    await userEvent.type(contactUrl, website)
  }

  return {
    contactPhoneNumber,
    contactMail,
    contactUrl,
    clearAndFillContact,
  }
}
