import mailjet from 'node-mailjet'

import {
  MAILJET_PRIVATE_API_KEY,
  MAILJET_PUBLIC_API_KEY,
  MAILJET_NOT_YET_ELIGIBLE_LIST_ID,
} from '../../utils/config'

export const addContactInNotYetEligibleList = (contactEmail, contactDepartmentCode, contactDateOfBirth) => {
  const mailjetClient = mailjet.connect(MAILJET_PUBLIC_API_KEY, MAILJET_PRIVATE_API_KEY)
  // TODO return Promise to resolve or reject
  return addNewContact(mailjetClient, contactEmail)
    .then(response => {
      const createdContactId = response.body.Data[0].ID
      // TODO parallelize with addContactInformations
      return addContactToList(mailjetClient, createdContactId, MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
    })
    .catch(error => {
      if (error.statusCode === 400) {
        // TODO get already existing contact id via mailjet client
        const contactId = undefined
        // TODO parallelize with addContactInformations
        return addContactToList(mailjetClient, contactId, MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
      }
    })
}

const addNewContact = (mailjetClient, email) =>
  mailjetClient
    .post('contact', { version: 'v3' })
    .request({
      Email: email,
    })

const addContactToList = (mailjetClient, contactId, listId) =>
  mailjetClient
    .post('listrecipient', { version: 'v3' })
    .request({
      IsUnsubscribed: 'false',
      ContactID: contactId,
      ListID: listId,
    })
    .then(() => addContactInformations(mailjetClient, contactId, '93', '26/02/2005'))
    .catch(error => {
      if (error.statusCode === 400) {
        return addContactInformations(mailjetClient, contactId, '93', '26/02/2005')
      }
    })

const addContactInformations = (mailjetClient, contactId, departmentCode, birthDate) => {
  // TODO convert birthDate to timestamp
  mailjetClient
    .put('contactdata', { version: 'v3' })
    .id(contactId)
    .request({
      Data: [
        {
          Name: 'date_de_naissance',
          Value: birthDate,
        },
        {
          Name: 'département',
          Value: departmentCode,
        },
      ],
    })
}
