import { screen } from '@testing-library/react'
import { useForm, FormProvider } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { SubcategoryIdEnum, WithdrawalTypeEnum } from 'apiClient/v1'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  venueListItemFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import {
  providedTicketWithdrawalTypeRadios,
  ticketWithdrawalTypeRadios,
} from 'pages/IndividualOffer/IndividualOfferInformations/commons/constants'
import { UsefulInformationFormValues } from 'pages/IndividualOffer/IndividualOfferInformations/commons/types'

import {
  UsefulInformationFormProps,
  UsefulInformationForm,
} from './UsefulInformationForm'

const MOCK = {
  nonRefundableSubcategory: subcategoryFactory({
    id: SubcategoryIdEnum.CINE_PLEIN_AIR,
    reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
  }),
  nonEventOnlineSubcategory: subcategoryFactory({
    id: SubcategoryIdEnum.ABO_LIVRE_NUMERIQUE,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  eventOfflineSubcategory: subcategoryFactory({
    id: SubcategoryIdEnum.EVENEMENT_CINE,
    isEvent: true,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  nonEventOfflineSubcategory: subcategoryFactory({
    id: SubcategoryIdEnum.LIVRE_PAPIER,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  withdrawableSubcategory: subcategoryFactory({
    id: SubcategoryIdEnum.CONCERT,
    canBeWithdrawable: true,
  }),
}

const LABELS = {
  sectionTitles: {
    location: /Où profiter de l’offre ?/,
    withdrawal: /Retrait de l’offre/,
    externalReservation: /Lien de réservation externe en l’absence de crédit/,
    accessibility: /Modalités d’accessibilité/,
    notifications: /Notifications/,
  },
  fields: {
    offerLocation: /Choisissez l’adresse à laquelle le public devra se présenter : */
  },
  withdrawalDetails: /Informations de retrait/,
  noRefundWarning: /Cette offre numérique ne sera pas remboursée./,
  withdrawalReminderCGU: /La livraison d’article est interdite/,
  bookingContact: /Email de contact/,
  withdrawalTypeLegend: /Précisez la façon dont vous distribuerez les billets/,
  withdrawalDateDelay: /Date d’envoi/,
  withdrawalHourDelay: /Heure de retrait/,
  externalReservation: /URL de votre site ou billetterie/,
  accessibilityLegend:
    /Cette offre est accessible au public en situation de handicap/,
  notificationCheckbox: /Être notifié par email des réservations/,
  notificationEmail: /Email auquel envoyer les notifications/,
}

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
    bulkCreateEventStocks: vi.fn(),
  },
}))

const renderUsefulInformationForm = (
  {
    props,
    contextValue,
    formValues,
    options,
  }: {
    props?: Partial<UsefulInformationFormProps>
    contextValue?: Partial<IndividualOfferContextValues>
    formValues?: Partial<UsefulInformationFormValues>
    options?: RenderWithProvidersOptions
  } = {
    props: {},
    contextValue: {},
    formValues: {},
    options: {},
  }
) => {
  const finalProps: UsefulInformationFormProps = {
    conditionalFields: [],
    selectedVenue: venueListItemFactory(),
    ...props,
  }

  const finalFormValues: UsefulInformationFormValues = {
    accessibility: {
      audio: false,
      mental: false,
      motor: false,
      visual: false,
      none: true,
    },
    addressAutocomplete: '',
    banId: '',
    bookingContact: '',
    bookingEmail: '',
    city: '',
    coords: '',
    externalTicketOfficeUrl: '',
    inseeCode: '',
    isEvent: false,
    isNational: false,
    latitude: '',
    locationLabel: '',
    longitude: '',
    manuallySetAddress: false,
    offerLocation: 'venueAddress',
    postalCode: '',
    receiveNotificationEmails: false,
    'search-addressAutocomplete': '',
    street: '',
    withdrawalDelay: '',
    withdrawalType: undefined,
    withdrawalDetails: '',
    ...formValues,
  }

  const finalContextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...contextValue,
  }

  const finalOptions: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...options,
  }

  const UsefulInformationFormWrapper = () => {
    const form = useForm<UsefulInformationFormValues>({
      defaultValues: finalFormValues,
    })

    return (
      <FormProvider {...form}>
        <UsefulInformationForm {...finalProps} />
      </FormProvider>
    )
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={{ ...finalContextValue }}>
      <UsefulInformationFormWrapper />
    </IndividualOfferContext.Provider>,
    finalOptions
  )
}

describe('UsefulInformationForm', () => {
  it('should render nothing in absence of offer', () => {
    renderUsefulInformationForm({
      contextValue: {
        offer: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: LABELS.sectionTitles.withdrawal })
    ).not.toBeInTheDocument()
  })

  it('should render a spinner in absence of selected venue', () => {
    renderUsefulInformationForm({
      props: {
        selectedVenue: undefined,
      },
    })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: LABELS.sectionTitles.withdrawal })
    ).not.toBeInTheDocument()
  })

  it('should render (without accessibility violations)', async () => {
    const { container } = renderUsefulInformationForm()

    expect(container).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.location,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.withdrawal,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.location,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.externalReservation,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.accessibility,
      })
    ).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  describe('when offer has an online subcategory', () => {
    it('should not render any offer location section', () => {
      renderUsefulInformationForm({
        contextValue: {
          offer: getIndividualOfferFactory({ subcategoryId: MOCK.nonEventOnlineSubcategory.id as SubcategoryIdEnum }),
          subCategories: [MOCK.nonEventOnlineSubcategory],
        },
      })

      expect(
        screen.queryByRole('group', {
          name: LABELS.fields.offerLocation,
        })
      ).not.toBeInTheDocument()
    })
  })

  describe('about withdrawal section', () => {
    it('should render a withdrawal information input', () => {
      renderUsefulInformationForm()

      expect(
        screen.getByRole('textbox', {
          name: LABELS.withdrawalDetails,
        })
      ).toBeInTheDocument()
    })

    describe('about refund warning', () => {
      it('should render when subcategory is not refundable', () => {
        renderUsefulInformationForm({
          contextValue: {
            offer: {
              ...getIndividualOfferFactory(),
              subcategoryId: MOCK.nonRefundableSubcategory
                .id as SubcategoryIdEnum,
            },
            subCategories: [MOCK.nonRefundableSubcategory],
          },
        })

        expect(screen.getByText(LABELS.noRefundWarning)).toBeInTheDocument()
      })
    })

    describe('about CGU withdrawal reminder', () => {
      it('should not render when offer is digital', () => {
        renderUsefulInformationForm({
          contextValue: {
            offer: {
              ...getIndividualOfferFactory(),
              isDigital: true,
              subcategoryId: MOCK.nonEventOnlineSubcategory.id as SubcategoryIdEnum,
            },
            subCategories: [MOCK.nonEventOnlineSubcategory],
          },
        })

        expect(
          screen.queryByText(LABELS.withdrawalReminderCGU)
        ).not.toBeInTheDocument()
      })

      it('should not render when offer is an event', () => {
        renderUsefulInformationForm({
          contextValue: {
            offer: {
              ...getIndividualOfferFactory(),
              subcategoryId: MOCK.eventOfflineSubcategory.id as SubcategoryIdEnum,
            },
            subCategories: [MOCK.eventOfflineSubcategory],
          },
        })

        expect(
          screen.queryByText(LABELS.withdrawalReminderCGU)
        ).not.toBeInTheDocument()
      })

      it('should render when offer is neiher digital nor an event', () => {
        renderUsefulInformationForm({
          contextValue: {
            offer: {
              ...getIndividualOfferFactory(),
              isDigital: false,
              subcategoryId: MOCK.nonEventOfflineSubcategory.id as SubcategoryIdEnum,
            },
            subCategories: [MOCK.nonEventOfflineSubcategory],
          },
        })

        expect(
          screen.getByText(LABELS.withdrawalReminderCGU)
        ).toBeInTheDocument()
      })
    })

    describe('when subcategory can be withdrawable', () => {
      it('should render a withdrawal type select', () => {
        renderUsefulInformationForm({
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
        })

        expect(
          screen.getByText(LABELS.withdrawalTypeLegend)
        ).toBeInTheDocument()
      })

      it('should render at a default set of withdrawal type options', () => {
        renderUsefulInformationForm({
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
        })

        const withdrawalTypeRadios = screen.getAllByRole('radio')
        expect(withdrawalTypeRadios.length).toBeGreaterThanOrEqual(
          ticketWithdrawalTypeRadios.length
        )

        for (const radio of ticketWithdrawalTypeRadios) {
          expect(
            screen.getByRole('radio', { name: radio.label })
          ).toBeInTheDocument()
        }
      })

      it('should render an extra withdrawal type option when withdrawalType is IN_APP', () => {
        renderUsefulInformationForm({
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
          formValues: {
            withdrawalType: WithdrawalTypeEnum.IN_APP,
          },
        })

        const withdrawalInAppRadion = providedTicketWithdrawalTypeRadios.find(
          (radio) => radio.value === WithdrawalTypeEnum.IN_APP
        )

        expect(
          screen.getByRole('radio', {
            name: withdrawalInAppRadion?.label,
          })
        ).toBeInTheDocument()
      })

      it('should render a withdrawal delay date select when withdrawal is by email', () => {
        renderUsefulInformationForm({
          formValues: {
            withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
          },
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
        })

        expect(
          screen.getByRole('combobox', {
            name: LABELS.withdrawalDateDelay,
          })
        ).toBeInTheDocument()
      })

      it('should render a withdrawal delay hour select when withdrawal is on site', () => {
        renderUsefulInformationForm({
          formValues: {
            withdrawalType: WithdrawalTypeEnum.ON_SITE,
          },
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
        })

        expect(
          screen.getByRole('combobox', {
            name: LABELS.withdrawalHourDelay,
          })
        ).toBeInTheDocument()
      })

      it('should render a booking contact email input', () => {
        renderUsefulInformationForm({
          props: {
            conditionalFields: [
              'withdrawalType',
              'withdrawalDelay',
              'bookingContact',
            ],
          },
        })

        expect(
          screen.getByRole('textbox', {
            name: LABELS.bookingContact,
          })
        ).toBeInTheDocument()
      })
    })
  })

  describe('about external reservation section', () => {
    it('should render an external reservation link input', () => {
      renderUsefulInformationForm()

      expect(
        screen.getByRole('textbox', {
          name: LABELS.externalReservation,
        })
      ).toBeInTheDocument()
    })
  })

  describe('about accessibility section', () => {
    it('should render an accessibility checkbox group', () => {
      renderUsefulInformationForm()

      expect(
        screen.getByRole('group', {
          name: LABELS.accessibilityLegend,
        })
      ).toBeInTheDocument()
    })
  })

  describe('about notifications section', () => {
    it('should render a notification checkbox', () => {
      renderUsefulInformationForm()

      expect(
        screen.getByRole('checkbox', {
          name: LABELS.notificationCheckbox,
        })
      ).toBeInTheDocument()
    })

    it('should render a booking email input when receiveNotificationEmails is true', () => {
      renderUsefulInformationForm({
        formValues: {
          receiveNotificationEmails: true,
        },
      })

      expect(
        screen.getByRole('textbox', {
          name: LABELS.notificationEmail,
        })
      ).toBeInTheDocument()
    })
  })
})
