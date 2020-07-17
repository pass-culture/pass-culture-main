import mailjet from 'node-mailjet'

import {
  MAILJET_PRIVATE_API_KEY,
  MAILJET_PUBLIC_API_KEY,
  MAILJET_NOT_YET_ELIGIBLE_LIST_ID,
} from '../../utils/config'

// TODO côté implem call cette fonction avec .then() et .catch()
export const addContactInNotYetEligibleList = (contactEmail, contactDepartmentCode, contactDateOfBirth) => {
  const mailjetClient = mailjet.connect(MAILJET_PUBLIC_API_KEY, MAILJET_PRIVATE_API_KEY)
  return new Promise((resolve, reject) => {
    addNewContact(mailjetClient, contactEmail)
      .then(response => {
        const createdContactId = response.body.Data[0].ID
        const addContactToListPromise = addContactToList(mailjetClient, createdContactId, MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
        const addContactInformationsPromise = addContactInformations(mailjetClient, createdContactId, '93', '26/02/2005')

        return Promise.all([addContactToListPromise, addContactInformationsPromise])
          .then(response => {
            resolve(response)
          })
          .catch(error => reject(error))
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
              reject('Error getting existing contact: ' + error.message)
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

const getExistingContact = (mailjetClient, email) => {
  const encodedEmail = encodeURI(email)
  return mailjetClient
    .get('contact', { 'version': 'v3' })
    .id(encodedEmail)
    .request()
}

const addContactToList = (mailjetClient, contactId, listId) => {
  return new Promise((resolve, reject) => {
    mailjetClient
      .post('listrecipient', { version: 'v3' })
      .request({
        IsUnsubscribed: 'false',
        ContactID: contactId,
        ListID: listId,
      })
      .then(response => {
        resolve(response)
      })
      .catch(error => {
        if (error.statusCode === 400) {
          resolve()
        }
        reject('Error adding contact to list: ' + error.message)
      })
  })
}

const addContactInformations = (mailjetClient, contactId, departmentCode, birthDate) => {
  const splittedBirthDate = birthDate.split('/')
  const birthDateTimeStampInSeconds = Date.UTC(splittedBirthDate[2], splittedBirthDate[1] - 1, splittedBirthDate[0]) / 1000

  return new Promise((resolve, reject) => {
    mailjetClient
      .put('contactdata', { version: 'v3' })
      .id(contactId)
      .request({
        Data: [
          {
            Name: 'date_de_naissance',
            Value: birthDateTimeStampInSeconds,
          },
          {
            Name: 'département',
            Value: departmentCode,
          },
        ],
      })
      .then(result => resolve(result))
      .catch(error => reject('Error adding contact informations: ' + error.message))
  })
}
