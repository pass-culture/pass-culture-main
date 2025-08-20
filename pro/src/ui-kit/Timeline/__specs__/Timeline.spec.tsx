import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Timeline, TimelineStepType } from '../Timeline'

function renderTimeline() {
  return render(
    <Timeline
      steps={[
        {
          type: TimelineStepType.SUCCESS,
          content: 'Step 1',
        },
        {
          type: TimelineStepType.SUCCESS,
          content: 'Step 2',
        },
        {
          type: TimelineStepType.WAITING,
          content: 'Step 3',
        },
        {
          type: TimelineStepType.DISABLED,
          content: 'Step 4',
        },
        {
          type: TimelineStepType.DISABLED,
          content: 'Step 5',
        },
        {
          type: TimelineStepType.ERROR,
          content: 'Step 6',
        },
      ]}
    />
  )
}

describe('Timeline', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderTimeline()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render without error', () => {
    renderTimeline()

    expect(screen.getByText('Step 1')).toBeInTheDocument()
  })
})
