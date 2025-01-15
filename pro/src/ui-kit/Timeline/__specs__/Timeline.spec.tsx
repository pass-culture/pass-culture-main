import { render, screen } from '@testing-library/react'

import { Timeline, TimelineStepType } from '../Timeline'

describe('Timeline', () => {
  it('should render without error', () => {
    render(
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

    expect(screen.getByText('Step 1')).toBeInTheDocument()
  })
})
