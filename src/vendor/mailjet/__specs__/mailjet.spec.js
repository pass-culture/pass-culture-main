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
    successfullCreationResponse
  beforeEach(() => {
    contactName = 'JeunePresqueEligible'
    contactEmail = 'jeunepresqueeligible@example.com'
    contactId = 2387456
    contactDepartmentCode = '93'
    contactDateOfBirth = '26/02/2005'
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
  })
  const addContactToListResponse = {
    body: {
      Data: [{
        Name: listName,
        ID: contactId,
      }]
    }
  }
  const addContactInformationsResponse = {
    body: {
      Data: [{
        IsExcludedFromCampaigns: true,
        Name: contactName,
        Email: contactEmail,
        ID: contactId,
      }]
    }
  }

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
})
