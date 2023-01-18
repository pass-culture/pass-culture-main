import type { Story } from '@storybook/react'
import React, { useState } from 'react'

import { Pagination, PaginationProps } from './Pagination'

export default {
  title: 'ui-kit/Pagination',
  component: Pagination,
}

const Template: Story<PaginationProps> = ({ currentPage, pageCount }) => {
  const [page, setPage] = useState(currentPage)

  return (
    <Pagination
      currentPage={page}
      pageCount={pageCount}
      onPreviousPageClick={() => setPage(page => page - 1)}
      onNextPageClick={() => setPage(page => page + 1)}
    />
  )
}

export const Default = Template.bind({})

Default.args = {
  currentPage: 3,
  pageCount: 10,
}
