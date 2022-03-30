import { IUseAnalyticsReturn } from '../useAnalytics'

const useAnalytics = (): IUseAnalyticsReturn => {
  return {
    logPageView: jest.fn(),
    logConsultCGUClick: jest.fn(),
    logPersonalDataClick: jest.fn(),
    logConsultSupportClick: jest.fn(),
    setAnalyticsUserId: jest.fn(),
    logTutoPageView: jest.fn(),
    logForgottenPasswordClick: jest.fn(),
    logHelpCenterClick: jest.fn(),
    logCreateVenueClick: jest.fn(),
    logCreateOfferClick: jest.fn(),
    logHomeClick: jest.fn(),
    logTicketClick: jest.fn(),
    logOfferClick: jest.fn(),
    logBookingClick: jest.fn(),
    logReimbursementClick: jest.fn(),
    logLogoutClick: jest.fn(),
    logProClick: jest.fn(),
  }
}

export default useAnalytics
