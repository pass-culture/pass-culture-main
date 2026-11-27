import { act, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { FormatEnum, NatureEnum } from '@/apiClient/v1'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setFormat, setNature } from '@/commons/store/nfd/reducer'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferV2 } from './IndividualOfferV2'

function Selection() {
  const { nature, format } = useAppSelector((state) => state.nfd)
  const dispatch = useAppDispatch()
  return (
    <>
      <output aria-label="Nature">{nature}</output>
      <output aria-label="Format">{format}</output>
      <button
        type="button"
        onClick={() => {
          dispatch(setNature(NatureEnum.BIEN))
          dispatch(setFormat(FormatEnum.LIVRE_PAPIER))
        }}
      >
        Choisir un livre
      </button>
    </>
  )
}

const renderSelection = async (
  initialPath = '/offre/individuelle/v2/creation/description'
) => {
  const children = [
    { path: 'description', element: <Selection /> },
    { path: 'nature-format-domaine', element: <Selection /> },
  ]
  const result = renderWithProviders(null, {
    initialRouterEntries: [initialPath],
    routes: [
      {
        path: '/offre/individuelle/v2/creation',
        element: <IndividualOfferV2 />,
        children,
      },
      {
        path: '/offre/individuelle/v2/:offerId/creation',
        element: <IndividualOfferV2 />,
        children,
      },
      { path: '/offres', element: <h1>Offres</h1> },
    ],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    },
  })
  await screen.findByRole('heading', { name: 'Créer une offre' })
  return result
}

describe('<IndividualOfferV2 />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
  })

  it('should keep nature and format in the store', async () => {
    const user = userEvent.setup()
    await renderSelection()

    await user.click(screen.getByRole('button', { name: 'Choisir un livre' }))
    expect(screen.getByLabelText('Nature')).toHaveTextContent(NatureEnum.BIEN)
    expect(screen.getByLabelText('Format')).toHaveTextContent(
      FormatEnum.LIVRE_PAPIER
    )
  })

  it('should reset the selection when leaving the creation flow', async () => {
    const user = userEvent.setup()
    const { router, store } = await renderSelection()

    await user.click(screen.getByRole('button', { name: 'Choisir un livre' }))
    await act(async () => {
      await router.navigate(
        '/offre/individuelle/v2/creation/nature-format-domaine'
      )
    })

    expect(store.getState().nfd).toEqual({
      nature: NatureEnum.BIEN,
      format: FormatEnum.LIVRE_PAPIER,
    })

    await act(async () => {
      await router.navigate('/offres')
    })
    expect(store.getState().nfd).toEqual({ nature: null, format: null })

    await act(async () => {
      await router.navigate('/offre/individuelle/v2/creation/description')
    })
    expect(screen.getByLabelText('Nature')).toBeEmptyDOMElement()
    expect(screen.getByLabelText('Format')).toBeEmptyDOMElement()
  })

  it('should link back to nature-format-domaine without offer id in the url when the offer is not created yet', async () => {
    await renderSelection()

    expect(
      screen.getByRole('link', { name: /Nature et format/ })
    ).toHaveAttribute(
      'href',
      '/offre/individuelle/v2/creation/nature-format-domaine'
    )
  })

  it('should link back to nature-format-domaine with the offer id in the url when editing a draft offer', async () => {
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      getIndividualOfferFactory({ id: 42 })
    )
    await renderSelection('/offre/individuelle/v2/42/creation/description')

    expect(
      screen.getByRole('link', { name: /Nature et format/ })
    ).toHaveAttribute(
      'href',
      '/offre/individuelle/v2/42/creation/nature-format-domaine'
    )
  })

  it('should have no accessibility violations', async () => {
    const { container } = await renderSelection()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should start with an empty selection', async () => {
    await renderSelection()

    expect(screen.getByLabelText('Nature')).toBeEmptyDOMElement()
    expect(screen.getByLabelText('Format')).toBeEmptyDOMElement()
  })

  it('should render its elements', async () => {
    await renderSelection()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Choisir un livre' })
    ).toBeInTheDocument()
    expect(screen.getByText('Tarif et modalités')).toBeInTheDocument()
  })
})
