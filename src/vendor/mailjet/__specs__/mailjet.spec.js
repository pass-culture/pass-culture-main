import mailjet from 'node-mailjet'
import { addContactInNotYetEligibleList } from '../mailjet'

jest.mock('node-mailjet', () => ({
  connect: undefined,
}))

jest.mock('../../../utils/config', () => ({
  MAILJET_PUBLIC_API_KEY: 'mailjetPublicApiKey',
  MAILJET_PRIVATE_API_KEY: 'mailjetPrivateApiKey',
  MAILJET_NOT_YET_ELIGIBLE_LIST_ID: 'notYetEligibleListId',
}))

describe('mailjet', () => {
  let mockMJRequest,
    mockMJPost,
    mockMJPut,
    mockMJGet,
    mockMJId,
    mockMJConnect,
    contactName,
    contactEmail,
    contactId,
    contactDepartmentCode,
    contactDateOfBirth,
    listName,
    successfullCreationResponse,
    addContactToListResponse,
    addContactInformationsResponse
  beforeEach(() => {
    contactName = 'JeunePresqueEligible'
    contactEmail = 'jeunepresqueeligible@example.com'
    contactId = 2387456
    contactDepartmentCode = '93'
    contactDateOfBirth = 1109376000
    listName = 'Liste Jeune Presque Eligible'
    mockMJRequest = jest.fn()
    mockMJId = jest.fn().mockReturnValue({ request: mockMJRequest })
    mockMJPut = jest.fn().mockReturnValue({ id: mockMJId })
    mockMJPost = jest.fn().mockReturnValue({ request: mockMJRequest })
    mockMJGet = jest.fn().mockReturnValue({ id: mockMJId })
    mockMJConnect = jest.fn().mockReturnValue({ post: mockMJPost, put: mockMJPut, get: mockMJGet })
    mailjet.connect = mockMJConnect
    successfullCreationResponse = {
      body: { Data: [{ ID: contactId }] },
    }

    addContactToListResponse = {
      body: {
        Data: [{
          Name: listName,
          ID: contactId,
        }]
      }
    }

    addContactInformationsResponse = {
      body: {
        Data: [{
          IsExcludedFromCampaigns: true,
          Name: contactName,
          Email: contactEmail,
          ID: contactId,
        }]
      }
    }
  })

  describe('when contact does not exist', () => {
    beforeEach(() => {
      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
      mockMJRequest.mockResolvedValueOnce(addContactToListResponse)
      mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
    })

    it('should connect to mailjet with credentials', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJConnect).toHaveBeenCalledWith('mailjetPublicApiKey', 'mailjetPrivateApiKey')
    })

    it('should save contact email adress', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJPost).toHaveBeenCalledWith('contact', { version: 'v3' })
      expect(mockMJRequest).toHaveBeenCalledWith({
        Email: contactEmail,
      })
    })

    it('should add new contact in soon to be eligible list', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJPost).toHaveBeenNthCalledWith(2, 'listrecipient', { version: 'v3' })
      expect(mockMJRequest).toHaveBeenNthCalledWith(2, {
        IsUnsubscribed: 'false',
        ContactID: contactId,
        ListID: 'notYetEligibleListId',
      })
    })

    it('should save contact date of birth and department code', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJPut).toHaveBeenCalledWith('contactdata', { version: 'v3' })
      expect(mockMJId).toHaveBeenCalledWith(contactId)
      expect(mockMJRequest).toHaveBeenNthCalledWith(3, {
        Data: [
          { Name: 'date_de_naissance', Value: contactDateOfBirth },
          { Name: 'département', Value: contactDepartmentCode },
        ],
      })
    })
  })

  describe('when contact already exists', () => {
    beforeEach(() => {
      const contactAlreadyExistsReponse = {
        statusCode: 400,
      }
      const getExistingContactResponse = {
        body: {
          Data: [{
            ID: contactId
          }]
        }
      }

      mockMJRequest.mockRejectedValueOnce(contactAlreadyExistsReponse)
      mockMJRequest.mockResolvedValueOnce(getExistingContactResponse)
      mockMJRequest.mockResolvedValueOnce(addContactToListResponse)
      mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
    })

    it('should get existing contact id', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJGet).toHaveBeenNthCalledWith(1, 'contact', { version: 'v3' })
      expect(mockMJRequest).toHaveBeenCalledTimes(4)
    })

    it('should add already existing contact in soon to be eligible list', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJPost).toHaveBeenNthCalledWith(2, 'listrecipient', { version: 'v3' })
      expect(mockMJRequest).toHaveBeenNthCalledWith(3, {
        IsUnsubscribed: 'false',
        ContactID: contactId,
        ListID: 'notYetEligibleListId',
      })
    })

    it('should save contact department code and date of birth', async () => {
      // When
      await addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // Then
      expect(mockMJPut).toHaveBeenCalledWith('contactdata', { version: 'v3' })
      expect(mockMJId).toHaveBeenCalledWith(contactId)
      expect(mockMJRequest).toHaveBeenNthCalledWith(4, {
        Data: [
          { Name: 'date_de_naissance', Value: contactDateOfBirth },
          { Name: 'département', Value: contactDepartmentCode },
        ],
      })
    })
  })

  describe('when unable to get existing contact', () => {
    beforeEach(() => {
      const contactAlreadyExistsReponse = {
        statusCode: 400,
      }
      const cannotGetExistingContactResponse = {
        statusCode: 400,
        message: 'error contact'
      }

      mockMJRequest.mockRejectedValueOnce(contactAlreadyExistsReponse)
      mockMJRequest.mockRejectedValueOnce(cannotGetExistingContactResponse)
      mockMJRequest.mockResolvedValueOnce(addContactToListResponse)
      mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
    })

    it('should catch an error', async () => {
      // when
      const result = addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // then
      await expect(result).rejects.toStrictEqual('Error getting existing contact: error contact')
    })
  })

  describe('when unable to save contact department code and date of birth', () => {
    beforeEach(() => {
      const cannotAddContactInformationResponse = {
        message: 'Error',
        status: 500
      }

      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
      mockMJRequest.mockResolvedValueOnce(addContactToListResponse)
      mockMJRequest.mockRejectedValueOnce(cannotAddContactInformationResponse)
    })

    it('should catch an error', async () => {
      // when
      const result = addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // then
      await expect(result).rejects.toStrictEqual('Error adding contact informations: Error')
    })
  })

  describe('when unable to add contact to list', () => {
    describe('when unable because contact already in mailing list', () => {
      beforeEach(() => {
        const cannotAddContactToListResponse = {
          statusCode: 400
        }

        mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
        mockMJRequest.mockRejectedValueOnce(cannotAddContactToListResponse)
        mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
      })

      it('should still resolve', async () => {
        // when
        const result = addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

        // then
        // eslint-disable-next-line jest/no-expect-resolves
        await expect(result).resolves.toStrictEqual([undefined, addContactInformationsResponse])
      })
    })

    describe('when unable because internal error', () => {
      beforeEach(() => {
        const cannotAddContactToListResponse = {
          statusCode: 500,
          message: 'error'
        }

        mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
        mockMJRequest.mockRejectedValueOnce(cannotAddContactToListResponse)
        mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
      })

      it('should catch an error', async () => {
        // when
        const result = addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

        // then
        await expect(result).rejects.toStrictEqual('Error adding contact to list: error')
      })
    })
  })

  describe('when everything success', () => {
    beforeEach(() => {
      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
      mockMJRequest.mockResolvedValueOnce(addContactToListResponse)
      mockMJRequest.mockResolvedValueOnce(addContactInformationsResponse)
    })

    it('should resolve', async () => {
      // when
      const result = addContactInNotYetEligibleList(contactEmail, contactDepartmentCode, contactDateOfBirth)

      // then
      // eslint-disable-next-line jest/no-expect-resolves
      await expect(result).resolves.toStrictEqual(  [
          {
            "body":
              {
                "Data": [
                  {
                    "ID": 2387456,
                    "Name": "Liste Jeune Presque Eligible"
                  }
                ]
              }
          },
          {
            "body":
              {
                "Data": [
                  {
                    "Email": "jeunepresqueeligible@example.com",
                    "ID": 2387456,
                    "IsExcludedFromCampaigns": true,
                    "Name": "JeunePresqueEligible"
                  }
                ]
              }
          }
        ]
      )
    })
  })
})
