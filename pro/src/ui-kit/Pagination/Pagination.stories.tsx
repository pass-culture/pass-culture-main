import type { Story } from '@storybook/react'
import React, { useCallback, useState } from 'react'

import { Pagination, PaginationProps } from './Pagination'

export default {
  title: 'ui-kit/Pagination',
  component: Pagination,
}

const Template: Story<PaginationProps> = ({ currentPage, pageCount }) => {
  const [page, setPage] = useState(currentPage)
  const previousPage = useCallback(() => setPage(page => page - 1), [])
  const nextPage = useCallback(() => setPage(page => page + 1), [])

  return (
    <Pagination
      currentPage={page}
      pageCount={pageCount}
      onPreviousPageClick={previousPage}
      onNextPageClick={nextPage}
    />
  )
}

export const Default = Template.bind({})

Default.args = {
  currentPage: 3,
  pageCount: 10,
}
