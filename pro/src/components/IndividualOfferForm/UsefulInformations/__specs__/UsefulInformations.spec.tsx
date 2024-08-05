import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import * as yup from 'yup'

import {
  GetOffererNameResponseModel,
  WithdrawalTypeEnum,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { setDefaultInitialFormValues } from 'components/IndividualOfferForm/utils/setDefaultInitialFormValues'
import { REIMBURSEMENT_RULES } from 'core/Finances/constants'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { Button } from 'ui-kit/Button/Button'
import {
  getOffererNameFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  UsefulInformations,
  UsefulInformationsProps,
} from '../UsefulInformations'
import { validationSchema } from '../validationSchema'

const renderUsefulInformations = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: Partial<IndividualOfferFormValues>
  onSubmit: () => void
  props: UsefulInformationsProps
}) => {
  return renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <UsefulInformations {...props} />
        <Button type="submit" isLoading={false}>
          Submit
        </Button>
      </Form>
    </Formik>
  )
}

describe('IndividualOffer section: UsefulInformations', () => {
  let initialValues: Partial<IndividualOfferFormValues>
  let props: UsefulInformationsProps
  const onSubmit = vi.fn()
  const offererId = 1
  let venueList: VenueListItemResponseModel[]

  beforeEach(() => {
    const offererNames: GetOffererNameResponseModel[] = [
      getOffererNameFactory({
        id: offererId,
        name: 'Offerer AE',
      }),
    ]

    venueList = [
      venueListItemFactory({
        isVirtual: false,
      }),
      venueListItemFactory({
        isVirtual: true,
      }),
    ]
    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      null,
      venueList,
      true
    )
    props = {
      offererNames,
      venueList,
      isUserAdmin: false,
      isVenueVirtual: false,
    }
  })

  it('should render the component', () => {
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    expect(
      screen.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Rayonnement national')
    ).not.toBeInTheDocument()
  })

  it('should submit valid form', async () => {
    initialValues.subcategoryId = 'CONCERT'
    initialValues.subCategoryFields = ['withdrawalType', 'bookingContact']
    props.offerSubCategory = subcategoryFactory({
      id: 'CONCERT',
      canBeWithdrawable: true,
    })
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    const venueSelect = screen.getByLabelText('Lieu *')
    await userEvent.selectOptions(venueSelect, venueList[0].id.toString())
    const withEmail = screen.getByLabelText(
      'Les billets seront envoyés par email'
    )
    await userEvent.click(withEmail)

    const bookingContactField = screen.getByLabelText('Email de contact *')
    await userEvent.type(bookingContactField, 'robertoDu36@example.com')

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        bookingContact: 'robertoDu36@example.com',
        accessibility: {
          audio: true,
          mental: true,
          motor: true,
          none: false,
          visual: true,
        },
        isVenueVirtual: false,
        offererId: offererId.toString(),
        subCategoryFields: ['withdrawalType', 'bookingContact'],
        url: '',
        subcategoryId: 'CONCERT',
        venueId: venueList[0].id.toString(),
        withdrawalDelay: (60 * 60 * 24).toString(),
        withdrawalDetails: '',
        withdrawalType: 'by_email',
      }),
      expect.anything()
    )
  })

  it('should submit valid form if initialValues has been given', async () => {
    initialValues = {
      ...initialValues,
      name: 'Set offer',
      venueId: 'AAAA',
      offererId: 'AE',
      subcategoryId: 'CONCERT',
      subCategoryFields: ['withdrawalType'],
      withdrawalDelay: 7200,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
    }

    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Set offer',
        offererId: 'AE',
        subCategoryFields: ['withdrawalType'],
        url: '',
        subcategoryId: 'CONCERT',
        venueId: 'AAAA',
        withdrawalDelay: 7200,
        withdrawalDetails: '',
        withdrawalType: WithdrawalTypeEnum.ON_SITE,
      }),
      expect.anything()
    )
  })

  it('should contain isNational when user is admin', () => {
    props.isUserAdmin = true
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(screen.getByLabelText('Rayonnement national')).toBeInTheDocument()
  })

  it('should contain withdrawal ticket informations when subcategory is from specific subCategory', async () => {
    initialValues.subcategoryId = 'CONCERT'
    initialValues.subCategoryFields = ['withdrawalType']
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      screen.getByText('Précisez la façon dont vous distribuerez les billets :')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Les billets seront envoyés par email')
    )
    screen.queryByLabelText('Date d’envoi *')
  })

  it('should contain withdrawal ticket informations when offer contain withrawalType informations', () => {
    // such a case is possible for all event public api/providers offers creation
    // even if they are not "canBeWithrawable"
    initialValues.withdrawalType = WithdrawalTypeEnum.NO_TICKET
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      screen.getByText('Précisez la façon dont vous distribuerez les billets :')
    ).toBeInTheDocument()
  })

  it('should not contain withdrawal ticket informations when subcategory is not from specific subCategory', () => {
    initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      screen.queryByText(
        'Précisez la façon dont vous distribuerez les billets :'
      )
    ).not.toBeInTheDocument()
  })

  it('should contain error if actor try to put a passculture mail', async () => {
    initialValues.subcategoryId = 'CONCERT'
    initialValues.subCategoryFields = ['withdrawalType', 'bookingContact']
    props.offerSubCategory = subcategoryFactory({
      id: 'CONCERT',
      canBeWithdrawable: true,
    })
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    const venueSelect = screen.getByLabelText('Lieu *')
    await userEvent.selectOptions(venueSelect, venueList[0].id.toString())
    const withEmail = screen.getByLabelText(
      'Les billets seront envoyés par email'
    )
    await userEvent.click(withEmail)

    const bookingContactField = screen.getByLabelText('Email de contact *')
    await userEvent.type(bookingContactField, 'robertoDu36@PASSculture.app')

    await userEvent.click(await screen.findByText('Submit'))

    expect(screen.getByText('Ce mail doit vous appartenir')).toBeInTheDocument()
  })

  describe('When venue is virtual', () => {
    beforeEach(() => {
      props.isVenueVirtual = true
      props.offerSubCategory = subcategoryFactory({
        id: 'VIRTUAL_SUB_CATEGORY',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      })
      initialValues.subcategoryId = 'VIRTUAL_SUB_CATEGORY'
      initialValues.venueId = 'BBBB'
    })

    it('should submit valid form', async () => {
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      const venueSelect = screen.getByLabelText('Lieu *')
      await userEvent.selectOptions(venueSelect, venueList[1].id.toString())

      const urlField = await screen.findByLabelText('URL d’accès à l’offre *')

      // deactivate type interpolation : https://testing-library.com/docs/ecosystem-user-event/#keyboardtext-options
      await userEvent.type(
        urlField,
        'https://example.com/routes?params={{offerId}'
      )
      await userEvent.click(await screen.findByText('Submit'))

      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          accessibility: {
            audio: true,
            mental: true,
            motor: true,
            none: false,
            visual: true,
          },
          isVenueVirtual: true,
          offererId: offererId.toString(),
          subCategoryFields: [],
          subcategoryId: 'VIRTUAL_SUB_CATEGORY',
          url: 'https://example.com/routes?params={offerId}',
          venueId: venueList[1].id.toString(),
          withdrawalDelay: undefined,
          withdrawalDetails: '',
          withdrawalType: undefined,
        }),
        expect.anything()
      )
    })

    it('should display url field with errors if needed', async () => {
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      const venueSelect = screen.getByLabelText('Lieu *')
      await userEvent.selectOptions(venueSelect, venueList[1].id.toString())

      const urlField = await screen.findByLabelText('URL d’accès à l’offre *')
      await userEvent.click(urlField)
      await userEvent.tab()

      expect(
        await screen.findByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()

      await userEvent.type(
        urlField,
        'https://example.com/routes?params={offerId}'
      )
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).not.toBeInTheDocument()

      await userEvent.clear(urlField)
      await userEvent.type(urlField, 'FAKE_URL')
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()
    })
  })

  describe('banners', () => {
    it('should display not reimbursment banner when subcategory is not reimbursed', () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = subcategoryFactory({
        reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
      })
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      expect(
        screen.queryByText('Cette offre numérique ne sera pas remboursée.')
      ).toBeInTheDocument()
      expect(
        screen.queryByText(
          'Quelles sont les offres numériques éligibles au remboursement ?'
        )
      ).toHaveAttribute(
        'href',
        'https://aide.passculture.app/hc/fr/articles/6043184068252'
      )
    })

    it('should not display not reimbursment banner when subcategory is reimbursed', () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = subcategoryFactory({
        reimbursementRule: REIMBURSEMENT_RULES.BOOK,
      })
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      expect(
        screen.queryByText(
          'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
        )
      ).not.toBeInTheDocument()
    })

    it('should display withdrawal banner when subcategory is on physical thing (not event, not virtual)', () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = subcategoryFactory({
        isEvent: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      })
      props.isVenueVirtual = false
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      expect(
        screen.queryByText(
          'La livraison d’article est interdite. Pour plus d’informations, veuillez consulter nos CGU.'
        )
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Consulter les Conditions Générales d'Utilisation")
      ).toHaveAttribute('href', 'https://pass.culture.fr/cgu-professionnels/')
    })

    it('should not display withdrawal banner when subcategory is an event', () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = subcategoryFactory({
        isEvent: true,
      })
      props.isVenueVirtual = false
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      expect(
        screen.queryByText(
          'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
        )
      ).not.toBeInTheDocument()
    })
  })

  describe('infobox', () => {
    describe('for not virtual offers', () => {
      it('should render the component', () => {
        renderUsefulInformations({
          initialValues,
          onSubmit,
          props,
        })

        const infoBox = screen.getByText(
          'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre. En renseignant ces informations depuis votre page lieu, elles s’appliqueront par défaut à toutes vos offres.'
        )
        const infoLink = screen.getByText(
          'Quelles modalités de retrait choisir ?'
        )
        expect(infoBox).toBeInTheDocument()
        expect(infoLink).toHaveAttribute(
          'href',
          'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-'
        )
      })
    })
    describe('for virtual offers', () => {
      it('should render the component', () => {
        props.isVenueVirtual = true

        renderUsefulInformations({
          initialValues,
          onSubmit,
          props,
        })

        const infoBoxWithdrawal = screen.getByText(
          'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre.'
        )
        const infoLinkWithdrawal = screen.getByText(
          'Quelles modalités de retrait choisir ?'
        )
        expect(infoBoxWithdrawal).toBeInTheDocument()
        expect(infoLinkWithdrawal).toHaveAttribute(
          'href',
          'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-'
        )
        const infoBoxUrl = screen.getByText(
          'Lien vers lequel seront renvoyés les bénéficiaires ayant réservé votre offre sur l’application pass Culture.'
        )
        expect(infoBoxUrl).toBeInTheDocument()
      })
    })
  })
})
