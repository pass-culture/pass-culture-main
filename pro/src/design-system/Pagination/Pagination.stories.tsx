import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { useState } from 'react'
import { Pagination } from './Pagination'

export default {
  title: '@/design-system/Pagination',
  decorators: [withRouter],
  component: Pagination,
}

export const FirstPage: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 1,
    pageCount: 7,
  }
}

export const LastPage: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 7,
    pageCount: 7,
  }
}

export const LotsOfPages: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 1,
    pageCount: 42,
  }
}

export const LotsOfPagesLast: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 42,
    pageCount: 42,
  }
}

export const LotsOfPagesMiddle: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 13,
    pageCount: 42,
  }
}

export const MobileViewForced: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true,
  }
}

export const Playground: StoryObj<typeof Pagination> = {
  args: {
    currentPage: 1,
    pageCount: 8,
    forceMobile: false,
  },
  render: (args) => {
    const [currentPage, setCurrentPage] = useState(args.currentPage);
    const [pageCount, setPageCount] = useState(args.pageCount);
    const [forceMobile, setForceMobile] = useState(args.forceMobile);

    const safePageCount = Number.isNaN(pageCount) ? args.pageCount : pageCount;
    return (
      <>
        (You can click on any page)
        <br />
        <br />
        <Pagination currentPage={currentPage} pageCount={safePageCount} onPageClick={(page) => setCurrentPage(page)} forceMobile={forceMobile} />
        
        <br />
        <fieldset>
          <legend>DEMO SETTINGS :</legend>

          <div>
            <label htmlFor="demo_pageCount">Page count :</label>{' '}
            <input id="demo_pageCount" type="number" min="1" onChange={(e) => setPageCount(parseInt(e.target.value))} value={pageCount} />
          </div>

          <div>
            <label htmlFor='demo_forceMobile'>Force mobile view :</label>{' '}
            <input id="demo_forceMobile" type="checkbox" onChange={(e) => setForceMobile(e.target.checked)} checked={forceMobile} />
          </div>
          
        </fieldset>
      </>
    )
  }
}