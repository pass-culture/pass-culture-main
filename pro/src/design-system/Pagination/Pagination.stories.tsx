import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { useState } from 'react'
import { Pagination } from './Pagination'

export default {
  title: '@/design-system/Pagination',
  decorators: [withRouter],
  component: Pagination,
}

export const Default: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 1,
    pageCount: 8,
  },
  render: (args) => {
    const [currentPage, setCurrentPage] = useState(args.currentPage);
    const [pageCount, setPageCount] = useState(args.pageCount);

    return (
      <>
        <Pagination currentPage={currentPage} pageCount={pageCount} onPageClick={(page) => setCurrentPage(page)} />
        <br/>
        Page count : <input type="number" onChange={(e) => setPageCount(parseInt(e.target.value))} value={pageCount} />
      </>
    )
  }
}
