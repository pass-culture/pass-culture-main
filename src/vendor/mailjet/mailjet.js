import mailjet from 'node-mailjet'

import {
  MAILJET_PRIVATE_API_KEY,
  MAILJET_PUBLIC_API_KEY,
  MAILJET_NOT_YET_ELIGIBLE_LIST_ID,
} from '../../utils/config'

export const addContactInNotYetEligibleList = (contactEmail, contactDepartmentCode, contactDateOfBirth) => {
  const mailjetClient = mailjet.connect(MAILJET_PUBLIC_API_KEY, MAILJET_PRIVATE_API_KEY)
  // TODO return Promise to resolve or reject
  return new Promise((resolve, reject) => {
    addNewContact(mailjetClient, contactEmail)
      .then(response => {
        const createdContactId = response.body.Data[0].ID
        //TODO paralellize with addContactInformations
        const addContactToListPromise = addContactToList(mailjetClient, createdContactId, MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
        const addContactInformationsPromise = addContactInformations(mailjetClient, createdContactId, '93', '26/02/2005')

        return Promise.all([addContactToListPromise, addContactInformationsPromise]).then(result => {
          resolve(result)
        })
      })
      .catch(error => {
        if (error.statusCode === 400) {
          return getExistingContact(mailjetClient, contactEmail)
            .then(response => {
              const existingContactId = response.body.Data[0].ID
              const addContactToListPromise = addContactToList(mailjetClient, existingContactId, MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
              const addContactInformationsPromise = addContactInformations(mailjetClient, existingContactId, '93', '26/02/2005')

              return Promise.all([addContactToListPromise, addContactInformationsPromise]).then(result => {
                resolve(result)
              })
            })
            .catch(error => {
              reject(new Error('Error getting existing contact: ' + error))
            })
        }
      })
  })
}

const addNewContact = (mailjetClient, email) =>
  mailjetClient
    .post('contact', { version: 'v3' })
    .request({
      Email: email,
    })

//TODO encode url
const getExistingContact = (mailjetClient, email) =>
  mailjetClient
    .get('contact', {'version': 'v3'})
    .id(email)
    .request()

const addContactToList = (mailjetClient, contactId, listId) => {
  return new Promise((resolve, reject) => {
    mailjetClient
      .post('listrecipient', { version: 'v3' })
      .request({
        IsUnsubscribed: 'false',
        ContactID: contactId,
        ListID: listId,
      })
      .then(result => {
        resolve(result)
      })
      .catch(error => {
        if (error.statusCode === 400) {
          reject('oops 400')
        }
        reject('AddContactToListError: ' + error)
      })
  })
}

const addContactInformations = (mailjetClient, contactId, departmentCode, birthDate) => {
  // TODO convert birthDate to timestamp
  return new Promise((resolve, reject) => {
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
      .then(result => resolve(result))
      .catch(error => reject('Erreur addContactInformations: ' + error))
  })
}
