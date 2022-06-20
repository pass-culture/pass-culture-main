import React from 'react'
import { connectPagination } from 'react-instantsearch-dom'
import './Pagination.scss'

import { ReactComponent as ChevronIcon } from 'assets/chevron-cropped.svg'

import { getPages } from './pagination_calculator'

interface IPagination {
  currentRefinement: number
  nbPages: number
  refine: (page: number) => void
  createURL: (page: number) => string
}
const CustomPagination = ({
  currentRefinement,
  nbPages,
  refine,
  createURL,
}: IPagination) => {
  const pages = getPages(currentRefinement, nbPages)

  const increasePageNumber = (event: React.MouseEvent<SVGElement>) => {
    event.preventDefault()
    refine(Math.max(1, currentRefinement - 1))
  }

  const decreasePageNumber = (event: React.MouseEvent<SVGElement>) => {
    event.preventDefault()
    refine(Math.min(nbPages, currentRefinement + 1))
  }

  return (
    <span className="pagination-container">
      <button className="pagination-arrow" type="button">
        <ChevronIcon onClick={event => increasePageNumber(event)} />
      </button>
      <ul className="page-numbers">
        {pages.map(page =>
          typeof page === 'number' ? (
            <li className="page-number" key={page}>
              <a
                className={currentRefinement === page ? 'is-active' : undefined}
                href={createURL(page)}
                onClick={event => {
                  event.preventDefault()
                  refine(page)
                }}
              >
                {page}
              </a>
            </li>
          ) : (
            <span className="page-dots" key={page}>
              {page}
            </span>
          )
        )}
      </ul>
      <button className="pagination-arrow" type="button">
        <ChevronIcon onClick={event => decreasePageNumber(event)} />
      </button>
    </span>
  )
}

export const Pagination = connectPagination(CustomPagination)
