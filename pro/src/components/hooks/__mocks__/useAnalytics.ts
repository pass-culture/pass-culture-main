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
    logFaqClick: jest.fn(),
    logCreateAccountClick: jest.fn(),
    logCreateVenueClick: jest.fn(),
    logCreateOfferClick: jest.fn(),
  }
}

export default useAnalytics
