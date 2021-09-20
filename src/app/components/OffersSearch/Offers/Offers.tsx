import "./Offers.scss"
import React from "react"

import { ResultType, Role } from "utils/types"

import { Offer } from "./Offer"

export const Offers = ({
  userRole,
  results,
}: {
  userRole: Role;
  results: ResultType[];
}): JSX.Element => (
  <ul className="offers">
    {results.map((result) => (
      <Offer
        canPrebookOffers={userRole == Role.redactor}
        key={result.id.raw}
        result={result}
      />
    ))}
  </ul>
)
