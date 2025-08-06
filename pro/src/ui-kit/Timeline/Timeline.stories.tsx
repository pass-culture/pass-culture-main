import type { StoryObj } from '@storybook/react'

import { Timeline, TimelineStepType } from './Timeline'

export default {
  title: '@/ui-kit/Timeline',
  component: Timeline,
}

export const Default: StoryObj<typeof Timeline> = {
  args: {
    steps: [
      {
        type: TimelineStepType.SUCCESS,
        content: 'Tout s’est bien passé',
      },
      {
        type: TimelineStepType.SUCCESS,
        content: 'Ça a marché, nous sommes sauvés !',
      },
      {
        type: TimelineStepType.WAITING,
        content: 'En attente de validation par notre PO et UX préférée',
      },
      {
        type: TimelineStepType.DISABLED,
        content: 'Cette étape n’est pas encore disponible...',
      },
      {
        type: TimelineStepType.DISABLED,
        content: 'Celle-ci non plus d’ailleurs',
      },
    ],
  },
}

export const WithError: StoryObj<typeof Timeline> = {
  args: {
    steps: [
      {
        type: TimelineStepType.SUCCESS,
        content:
          'C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages',
      },
      {
        type: TimelineStepType.SUCCESS,
        content:
          'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"',
      },
      {
        type: TimelineStepType.SUCCESS,
        content: '"Jusqu’ici tout va bien"',
      },
      {
        type: TimelineStepType.SUCCESS,
        content: '"Jusqu’ici tout va bien"',
      },
      {
        type: TimelineStepType.SUCCESS,
        content: '"Jusqu’ici tout va bien"',
      },
      {
        type: TimelineStepType.ERROR,
        content: 'Mais l’important, c’est pas la chute. C’est l’atterrissage.',
      },
    ],
  },
}
