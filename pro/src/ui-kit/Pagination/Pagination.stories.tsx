import type { StoryObj } from '@storybook/react'

import { Pagination } from './Pagination'

export default {
  title: '@/ui-kit/Pagination',
  component: Pagination,
}

export const Default: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 3,
    pageCount: 10,
  },
}
