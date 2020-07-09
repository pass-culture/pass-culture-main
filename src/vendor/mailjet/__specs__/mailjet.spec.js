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
    mockMJId,
    mockMJConnect,
    contactEmail,
    contactId,
    contactDepartmentCode,
    contactDateOfBirth,
    successfullCreationResponse
  beforeEach(() => {
    contactEmail = 'jeunepresqueeligible@example.com'
    contactId = 2387456
    contactDepartmentCode = '93'
    contactDateOfBirth = '26/02/2005'
    mockMJRequest = jest.fn()
    mockMJId = jest.fn().mockReturnValue({ request: mockMJRequest })
    mockMJPut = jest.fn().mockReturnValue({ id: mockMJId })
    mockMJPost = jest.fn().mockReturnValue({ request: mockMJRequest })
    mockMJConnect = jest.fn().mockReturnValue({ post: mockMJPost, put: mockMJPut })
    mailjet.connect = mockMJConnect
    successfullCreationResponse = {
      body: { Data: [{ ID: contactId }] },
    }
  })

  describe('when contact does not exist', () => {
    beforeEach(() => {
      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
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
      mockMJRequest.mockRejectedValueOnce(contactAlreadyExistsReponse)
      mockMJRequest.mockResolvedValueOnce()
    })

    it('should add already existing contact in soon to be eligible list', async () => {
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

  describe('when contact in not already in soon to be eligible list', () => {
    beforeEach(() => {
      const successfullAdditionResponse = {
        body: {
          Data: [{ ListID: 'notYetEligibleListId' }],
        },
      }
      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
      mockMJRequest.mockResolvedValueOnce(successfullAdditionResponse)
    })

    it('should save contact department code and date of birth', async () => {
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

  describe('when contact is already in soon to be eligible list', () => {
    beforeEach(() => {
      mockMJRequest.mockResolvedValueOnce(successfullCreationResponse)
      mockMJRequest.mockRejectedValueOnce({ statusCode: 400 })
    })

    it('should save contact department code and date of birth', async () => {
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
})
