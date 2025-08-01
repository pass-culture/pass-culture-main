import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from 'commons/utils/factories/individualApiFactories'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import * as imageUploadModule from 'pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'

import {
  IndividualOfferMediaScreen,
  IndividualOfferMediaScreenProps,
} from './IndividualOfferMediaScreen'

// This is to avoid "Already caught: Warning:
// An update to IndividualOfferMediaScreen
// inside a test was not wrapped in act(...)."
const waitForScrollToFirstErrorHookUseEffect = async () => {
  await screen.findByRole('heading', {
    name: LABELS.mainSection,
  })
}

const renderIndividualOfferMediaScreen = async ({
  props = {},
  mode = OFFER_WIZARD_MODE.CREATION,
}: {
  props?: Partial<IndividualOfferMediaScreenProps>
  mode?: OFFER_WIZARD_MODE
} = {}) => {
  const finalOffer = getIndividualOfferFactory(props.offer)
  const finalContextValue: IndividualOfferContextValues =
    individualOfferContextValuesFactory({ offer: finalOffer })

  const res = renderWithProviders(
    <IndividualOfferContext.Provider value={finalContextValue}>
      <IndividualOfferMediaScreen offer={finalOffer} />
    </IndividualOfferContext.Provider>,
    {
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
          mode,
          offerId: finalOffer.id,
        }),
      ],
    }
  )

  await waitForScrollToFirstErrorHookUseEffect()
  return res
}

const mockLogEvent = vi.fn()
const mockHandleImageOnSubmit = vi.fn()
const mockNavigate = vi.fn()
vi.mock('apiClient/api', () => ({
  api: {
    patchDraftOffer: vi.fn(),
  },
}))
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})
const MOCK_DATA = {
  videoUrl: 'https://www.youtube.com/watch?v=0R5PZxOgoz8',
}

const LABELS = {
  mainSection: 'Illustrez votre offre',
  imageSubSection: 'Ajoutez une image',
  imageInput: 'Importez une image',
  imageUpsertOrEditModalButton: 'Importer',
  videoSubSection: 'Ajoutez une vidéo',
  videoInput: 'Lien URL Youtube',
  videoError: 'Veuillez renseigner une URL provenant de la plateforme Youtube',
  previousButtonCreationMode: 'Retour',
  previousButtonEditionMode: 'Annuler et quitter',
  nextButtonCreationMode: 'Enregistrer et continuer',
  nextButtonEditionMode: 'Enregistrer les modifications',
}

const getSubmitLabel = (mode: OFFER_WIZARD_MODE) => {
  return mode === OFFER_WIZARD_MODE.CREATION
    ? LABELS.nextButtonCreationMode
    : LABELS.nextButtonEditionMode
}

const updateVideoUrlAndSubmit = async ({
  text = MOCK_DATA.videoUrl,
  mode = OFFER_WIZARD_MODE.CREATION,
}: {
  text?: string
  mode?: OFFER_WIZARD_MODE
} = {}) => {
  const videoInput = screen.getByRole('textbox', {
    name: LABELS.videoInput,
  })

  if (text) {
    await userEvent.type(videoInput, text)
  } else {
    await userEvent.clear(videoInput)
  }

  const label = getSubmitLabel(mode)
  await userEvent.click(screen.getByRole('button', { name: label }))
}

describe('IndividualOfferMediaScreen', () => {
  it('should render (without accessibility violations)', async () => {
    const { container } = await renderIndividualOfferMediaScreen()
    expect(container).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should always render an image input', async () => {
    await renderIndividualOfferMediaScreen()

    expect(screen.getByRole('heading', { name: LABELS.imageSubSection }))
    const input = screen.getByLabelText(LABELS.imageInput)
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'file')
  })

  it('should always render a video url input', async () => {
    await renderIndividualOfferMediaScreen()

    expect(screen.getByRole('heading', { name: LABELS.videoSubSection }))
    expect(screen.getByRole('textbox', { name: LABELS.videoInput }))
  })

  describe('about image (and credit)', () => {
    it('should log an event when an image is uploaded (drag or selected)', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      await renderIndividualOfferMediaScreen()

      const imageInput = screen.getByLabelText('Importez une image')
      await userEvent.upload(imageInput, new File(['fake img'], 'fake_img.jpg'))

      expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
        imageType: UploaderModeEnum.OFFER,
        imageCreationStage: 'add image',
      })
    })

    it('should not call the api handler until an image has been upserted', async () => {
      vi.spyOn(
        imageUploadModule,
        'useIndividualOfferImageUpload'
      ).mockReturnValue({
        hasUpsertedImage: false,
        handleImageOnSubmit: mockHandleImageOnSubmit,
      } as any)
      await renderIndividualOfferMediaScreen()

      await userEvent.click(screen.getByText(LABELS.nextButtonCreationMode))
      expect(mockHandleImageOnSubmit).not.toHaveBeenCalled()
    })

    it('should call the api handler when an image has been upserted', async () => {
      vi.spyOn(
        imageUploadModule,
        'useIndividualOfferImageUpload'
      ).mockReturnValue({
        hasUpsertedImage: true,
        handleImageOnSubmit: mockHandleImageOnSubmit,
      } as any)
      await renderIndividualOfferMediaScreen()

      await userEvent.click(screen.getByText(LABELS.nextButtonCreationMode))
      expect(mockHandleImageOnSubmit).toHaveBeenCalled()
    })

    describe('when the offer is product based', () => {
      it('should not allow any image update by disabling image input', async () => {
        await renderIndividualOfferMediaScreen({
          props: {
            offer: getIndividualOfferFactory({
              productId: 1,
            }),
          },
        })

        const input = screen.getByLabelText(LABELS.imageInput)
        expect(input).toBeDisabled()
      })
    })

    describe('when the offer is synchronized', () => {
      it('should allow image udpate', async () => {
        await renderIndividualOfferMediaScreen({
          props: {
            offer: getIndividualOfferFactory({
              lastProvider: { name: 'Provider Name' },
            }),
          },
        })

        const input = screen.getByLabelText(LABELS.imageInput)
        expect(input).not.toBeDisabled()
      })
    })
  })

  describe('about video url input', () => {
    it('should raise an error when video url has the wrong format & prevent submission', async () => {
      Element.prototype.scrollIntoView = vi.fn()
      await renderIndividualOfferMediaScreen()

      await updateVideoUrlAndSubmit({
        text: 'https://www.dailymotion.com/video/x9negsq',
      })

      const videoInput = screen.getByRole('textbox', {
        name: LABELS.videoInput,
      })
      expect(videoInput).toBeInvalid()
      const videoErrorMessage = screen.getByText(LABELS.videoError)
      expect(videoErrorMessage).toBeInTheDocument()
      expect(api.patchDraftOffer).not.toHaveBeenCalled()
    })

    it('should not call the patch offer api until the video url has changed', async () => {
      await renderIndividualOfferMediaScreen()

      await userEvent.click(screen.getByText(LABELS.nextButtonCreationMode))
      expect(api.patchDraftOffer).not.toHaveBeenCalled()
    })

    it('should call the patch offer api when the video url has changed', async () => {
      const knownOffer = getIndividualOfferFactory()
      await renderIndividualOfferMediaScreen({ props: { offer: knownOffer } })

      await updateVideoUrlAndSubmit()
      expect(api.patchDraftOffer).toHaveBeenCalledWith(knownOffer.id, {
        videoUrl: MOCK_DATA.videoUrl,
      })
    })

    it('should call the patch offer api when the video url has been deleted (empty string)', async () => {
      const knownOffer = getIndividualOfferFactory({
        videoUrl: MOCK_DATA.videoUrl,
      })
      await renderIndividualOfferMediaScreen({ props: { offer: knownOffer } })

      await updateVideoUrlAndSubmit({ text: '' })
      expect(api.patchDraftOffer).toHaveBeenCalledWith(knownOffer.id, {
        videoUrl: '',
      })
    })
  })

  describe('about navigation', () => {
    describe('previous step', () => {
      it('on creation mode, should go back to informations page', async () => {
        const knownOffer = getIndividualOfferFactory()
        await renderIndividualOfferMediaScreen({ props: { offer: knownOffer } })

        const previousButton = screen.getByRole('button', {
          name: LABELS.previousButtonCreationMode,
        })
        await userEvent.click(previousButton)
        expect(mockNavigate).toHaveBeenCalledWith(
          `/offre/individuelle/${knownOffer.id}/creation/pratiques`
        )
      })

      it('on edition mode, should go back to read-only mode', async () => {
        const knownOffer = getIndividualOfferFactory()
        await renderIndividualOfferMediaScreen({
          props: { offer: knownOffer },
          mode: OFFER_WIZARD_MODE.EDITION,
        })

        const previousButton = screen.getByRole('button', {
          name: LABELS.previousButtonEditionMode,
        })
        await userEvent.click(previousButton)
        expect(mockNavigate).toHaveBeenCalledWith(
          `/offre/individuelle/${knownOffer.id}/media`
        )
      })
    })

    describe('next step (successful submit)', () => {
      describe('on creation mode', () => {
        it('when the offer is an event, should go to tarifs page', async () => {
          const mode = OFFER_WIZARD_MODE.CREATION
          const eventOffer = getIndividualOfferFactory({ isEvent: true })
          await renderIndividualOfferMediaScreen({
            props: { offer: eventOffer },
            mode,
          })

          await updateVideoUrlAndSubmit({ mode })
          expect(mockNavigate).toHaveBeenCalledWith(
            `/offre/individuelle/${eventOffer.id}/creation/tarifs`
          )
        })

        it('when the offer is not an event, should go to stocks page', async () => {
          const mode = OFFER_WIZARD_MODE.CREATION
          const eventOffer = getIndividualOfferFactory({ isEvent: false })
          await renderIndividualOfferMediaScreen({
            props: { offer: eventOffer },
            mode,
          })

          await updateVideoUrlAndSubmit({ mode })
          expect(mockNavigate).toHaveBeenCalledWith(
            `/offre/individuelle/${eventOffer.id}/creation/stocks`
          )
        })
      })

      it('on edition mode, should go back to read-only mode', async () => {
        const mode = OFFER_WIZARD_MODE.EDITION
        const knownOffer = getIndividualOfferFactory()
        await renderIndividualOfferMediaScreen({
          props: { offer: knownOffer },
          mode,
        })

        await updateVideoUrlAndSubmit({ mode })
        expect(mockNavigate).toHaveBeenCalledWith(
          `/offre/individuelle/${knownOffer.id}/media`
        )
      })
    })
  })
})
