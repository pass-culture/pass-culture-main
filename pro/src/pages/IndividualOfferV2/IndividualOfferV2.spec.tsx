import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { FormatEnum, NatureEnum } from '@/apiClient/v1'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setFormat, setNature } from '@/commons/store/nfd/reducer'
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

const renderSelection = () =>
  renderWithProviders(null, {
    initialRouterEntries: ['/offre/individuelle/v2/creation/description'],
    routes: [
      {
        path: '/offre/individuelle/v2/creation',
        element: <IndividualOfferV2 />,
        children: [{ path: 'description', element: <Selection /> }],
      },
    ],
  })

describe('<IndividualOfferV2 />', () => {
  it('should keep nature and format in the store', async () => {
    const user = userEvent.setup()
    renderSelection()

    await user.click(screen.getByRole('button', { name: 'Choisir un livre' }))
    expect(screen.getByLabelText('Nature')).toHaveTextContent(NatureEnum.BIEN)
    expect(screen.getByLabelText('Format')).toHaveTextContent(
      FormatEnum.LIVRE_PAPIER
    )
  })

  it('should have no accessibility violations', async () => {
    const { container } = renderSelection()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should start with an empty selection', () => {
    renderSelection()

    expect(screen.getByLabelText('Nature')).toBeEmptyDOMElement()
    expect(screen.getByLabelText('Format')).toBeEmptyDOMElement()
  })

  it('should render its elements', () => {
    renderSelection()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Choisir un livre' })
    ).toBeInTheDocument()
    expect(screen.getByText('Tarif et modalités')).toBeInTheDocument()
  })
})
