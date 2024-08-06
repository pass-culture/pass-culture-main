import { screen } from '@testing-library/react'

import { Mode } from 'core/OfferEducational/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ActionsBarSticky } from '../ActionsBarSticky'

const renderActionsBar = ({
  dirtyForm,
  mode,
}: {
  dirtyForm?: boolean
  mode: Mode
}) =>
  renderWithProviders(
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <div>left content</div>
      </ActionsBarSticky.Left>

      <ActionsBarSticky.Right dirtyForm={dirtyForm} mode={mode}>
        <div>right content</div>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )

describe('ActionsBarSticky', () => {
  it('should render contents', () => {
    renderActionsBar({ dirtyForm: undefined, mode: Mode.EDITION })

    expect(screen.queryByText('left content')).toBeInTheDocument()
    expect(screen.queryByText('right content')).toBeInTheDocument()
  })

  it('should display the saved draft message', () => {
    renderActionsBar({ dirtyForm: false, mode: Mode.CREATION })

    expect(screen.queryByText('Brouillon enregistré')).toBeInTheDocument()
  })

  it('should display draft unsaved information message', () => {
    renderActionsBar({ dirtyForm: true, mode: Mode.CREATION })

    expect(screen.queryByText('Brouillon non enregistré')).toBeInTheDocument()
  })
})
