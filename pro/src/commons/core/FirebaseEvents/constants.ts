export enum Events {
  CLICKED_BOOKING = 'hasClickedBooking',
  CLICKED_CANCELED_SELECTED_OFFERS = 'hasClickedCancelOffers',
  CLICKED_DISABLED_SELECTED_OFFERS = 'hasClickedDisabledOffers',
  CLICKED_CONSULT_CGU = 'hasClickedConsultCGU',
  CLICKED_CONSULT_SUPPORT = 'hasClickedConsultSupport',
  CLICKED_CREATE_ACCOUNT = 'hasClickedCreateAccount',
  CLICKED_CREATE_VENUE = 'hasClickedCreateVenue',
  CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL = 'hasClickedSeeLaterFromSuccessVenueCreationModal',
  CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL = 'hasClickedSeeLaterFromSuccessOfferCreationModal',
  CLICKED_SAVE_VENUE = 'hasClickedSaveVenue',
  CLICKED_DOWNLOAD_BOOKINGS = 'hasClickedDownloadBooking',
  CLICKED_DOWNLOAD_BOOKINGS_CSV = 'hasClickedDownloadBookingCsv',
  CLICKED_DOWNLOAD_BOOKINGS_XLS = 'hasClickedDownloadBookingXls',
  CLICKED_EDIT_PROFILE = 'hasClickedEditProfile',
  CLICKED_EDIT_COLLECTIVE_OFFER = 'hasClickedEditCollectiveOffer',
  CLICKED_HOME_STATS_PENDING_OFFERS_FAQ = 'hasClickedHomeStatsPendingOffersFaq',
  CLICKED_FORGOTTEN_PASSWORD = 'hasClickedForgottenPassword',
  CLICKED_HELP_CENTER = 'hasClickedHelpCenter',
  CLICKED_HOME = 'hasClickedHome',
  CLICKED_LOGOUT = 'hasClickedLogout',
  CLICKED_CONFIRMED_ADD_HEADLINE_OFFER = 'hasClickedConfirmedAddHeadlineOffer',
  CLICKED_DISCOVERED_HEADLINE_OFFER = 'hasClickedDiscoveredHeadlineOffer',
  CLICKED_OFFER = 'hasClickedOffer',
  CLICKED_OFFER_FORM_NAVIGATION = 'hasClickedOfferFormNavigation',
  CLICKED_ONBOARDING_FORM_NAVIGATION = 'HasClickedOnboardingFormNavigation',
  CLICKED_CANCEL_OFFER_CREATION = 'hasClickedCancelOfferCreation',
  CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK = 'hasClickedPartnerBlockPreviewVenueLink',
  CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK = 'hasClickedPartnerBlockCopyVenueLink',
  CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK = 'hasClickedPartnerBlockDmsApplicationLink',
  CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK = 'hasClickedPartnerBlockCollectiveHelpLink',
  CLICKED_PERSONAL_DATA = 'hasClickedConsultPersonalData',
  CLICKED_PRO = 'hasClickedPro',
  CLICKED_REIMBURSEMENT = 'hasClickedReimbursement',
  CLICKED_SHOW_BOOKINGS = 'hasClickedShowBooking',
  CLICKED_STATS = 'hasClickedOffererStats',
  CLICKED_TICKET = 'hasClickedTicket',
  CLICKED_DUPLICATE_TEMPLATE_OFFER = 'hasClickedDuplicateTemplateOffer',
  CLICKED_DUPLICATE_BOOKABLE_OFFER = 'hasClickedDuplicateBookableOffer',
  CLICKED_BEST_PRACTICES_STUDIES = 'hasClickedBestPracticesAndStudies',
  CLICKED_HELP_LINK = 'hasClickedHelpLink',
  CLICKED_RESET_FILTERS = 'hasClickedResetFilter',
  CLICKED_SHOW_STATUS_FILTER = 'hasClickedShowStatusFilter',
  CLICKED_OMNI_SEARCH_CRITERIA = 'hasClickedOmniSearchCriteria',
  CLICKED_PAGINATION_NEXT_PAGE = 'hasClickedPaginationNextPage',
  CLICKED_PAGINATION_PREVIOUS_PAGE = 'hasClickedPaginationPreviousPage',
  CLICKED_CONTACT_OUR_TEAMS = 'hasClickedContactOurTeams',
  CLICKED_ARCHIVE_COLLECTIVE_OFFER = 'hasClickedArchiveCollectiveOffer',
  CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER = 'hasClickedSaveDraftAndExitCollectiveOffer',
  CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE = 'hasClickedSeeTemplateOfferExample',
  FIRST_LOGIN = 'firstLogin',
  PAGE_VIEW = 'page_view',
  SIGNUP_FORM_ABORT = 'signupFormAbort',
  SIGNUP_FORM_SUCCESS = 'signupFormSuccess',
  TUTO_PAGE_VIEW = 'tutoPageView',
  DELETE_DRAFT_OFFER = 'DeleteDraftOffer',
  CLICKED_NO_VENUE = 'hasClickedNoVenue',
  CLICKED_EAC_DMS_TIMELINE = 'hasClickedEacDmsTimeline',
  CLICKED_EAC_DMS_LINK = 'hasClickedEacDmsLink',
  CLICKED_CREATE_OFFER_FROM_REQUEST = 'hasClickedCreateOfferFromRequest',
  CLICKED_ADD_IMAGE = 'hasClickedAddImage',
  DRAG_OR_SELECTED_IMAGE = 'hasDragOrSelectedImage',
  CLICKED_SAVE_IMAGE = 'hasClickedSaveImage',
  CLICKED_DELETE_STOCK = 'hasClickedDeleteStock',
  CLICKED_BULK_DELETE_STOCK = 'hasClickedBulkDeleteStock',
  CLICKED_DOWNLOAD_OFFER_BOOKINGS = 'hasDownloadedBookings',
  CLICKED_PAGE_FOR_APP_HOME = 'hasClickedPageForAppHome',
  CLICKED_PAGE_FOR_ADAGE_HOME = 'hasClickedPageForAdageHome',
  CLICKED_INVOICES_DOWNLOAD = 'hasClickedInvoicesDownload',
  CLICKED_PUBLISH_FUTURE_OFFER_EARLIER = 'hasClickedPublishFutureOfferEarlier',
  EXTRA_PRO_DATA = 'extra_pro_data',
  CLICKED_NEW_EVOLUTIONS = 'hasClickedNewEvolutions',
  CLICKED_CONSULT_HELP = 'hasClickedConsultHelp',
  UPDATED_BOOKING_LIMIT_DATE = 'hasUpdatedBookingLimitDate',
  CLICKED_GENERATE_TEMPLATE_DESCRIPTION = 'hasClickedGenerateTemplateDescription',
  UPDATED_EVENT_STOCK_FILTERS = 'hasUpdatedEventStockFilters',
  CLICKED_VALIDATE_ADD_RECURRENCE_DATES = 'hasClickedValidateAddRecurrenceDates',
  FAKE_DOOR_VIDEO_INTERESTED = 'fakeDoorVideoInterested',
  CLICKED_SORT_STOCKS_TABLE = 'hasClickedSortStocksTable',
}

export enum VenueEvents {
  CLICKED_VENUE_ACCORDION_BUTTON = 'hasClickedVenueAccordionButton',
  CLICKED_VENUE_ADD_RIB_BUTTON = 'hasClickedVenueAddRibButton',
  CLICKED_VENUE_PUBLISHED_OFFERS_LINK = 'hasClickedVenuePublishedOffersLink',
}

export enum CollectiveBookingsEvents {
  CLICKED_DETAILS_BUTTON_CELL = 'hasClickedDetailsButtonCell',
  CLICKED_MODIFY_BOOKING_LIMIT_DATE = 'hasClickedModifyBookingLimitDate',
  CLICKED_SEE_COLLECTIVE_BOOKING = 'hasClickedSeeCollectiveBooking',
}

export enum OFFER_FORM_NAVIGATION_MEDIUM {
  OFFERS_TRASH_ICON = 'OffersTrashicon',
}

export enum OFFER_FORM_NAVIGATION_IN {
  HOME = 'Home',
  OFFERS = 'Offers',
}

export enum COLLECTIVE_OFFER_DUPLICATION_ENTRIES {
  OFFERS_MODAL = 'OffersListModal',
  OFFERS = 'OffersList',
  OFFER_RECAP = 'OfferRecap',
}

export enum SynchronizationEvents {
  CLICKED_SYNCHRONIZE_OFFER = 'hasClickedSynchronizeOffer',
  CLICKED_IMPORT = 'hasClickedImport',
  CLICKED_VALIDATE_IMPORT = 'hasClickedValidateImport',
}

export enum OffererLinkEvents {
  CLICKED_INVITE_COLLABORATOR = 'hasClickedInviteCollaborator',
  CLICKED_ADD_COLLABORATOR = 'hasClickedAddCollaborator',
  CLICKED_SEND_INVITATION = 'hasSentInvitation',
}

export enum BankAccountEvents {
  CLICKED_ADD_BANK_ACCOUNT = 'hasClickedAddBankAccount',
  CLICKED_ADD_VENUE_TO_BANK_ACCOUNT = 'HasClickedAddVenueToBankAccount',
  CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS = 'HasClickedHasBankAccountWithPendingCorrections',
  CLICKED_CHANGE_VENUE_TO_BANK_ACCOUNT = 'HasClickedChangeVenueToBankAccount',
  CLICKED_CONTINUE_TO_DS = 'HasClickedContinueToDS',
  CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP = 'HasClickedBankDetailsRecordFollowUp',
  CLICKED_SAVE_VENUE_TO_BANK_ACCOUNT = 'HasClickedSaveVenueToBankAccount',
}

export const OnboardingDidacticEvents = {
  HAS_CLICKED_START_COLLECTIVE_DIDACTIC_ONBOARDING:
    'hasClickedStartCollectiveDidacticOnboarding',
  HAS_CLICKED_ALREADY_SUBMITTED_COLLECTIVE_CASE_DIDACTIC_ONBOARDING:
    'hasClickedAlreadySubmittedCollectiveCaseDidacticOnboarding',
  HAS_CLICKED_SUBMIT_COLLECTIVE_CASE_DIDACTIC_ONBOARDING:
    'hasClickedSubmitCollectiveCaseDidacticOnboarding',
}
