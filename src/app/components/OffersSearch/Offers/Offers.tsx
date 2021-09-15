import "./Offers.scss"
import React from "react"

import { Notification } from "app/components/Layout/Notification/Notification"
import { ResultType, Role } from "utils/types"

import { Offer } from "./Offer"

export const Offers = ({
  notify,
  userRole,
  results,
}: {
  notify: (notification: Notification) => void;
  userRole: Role;
  results: ResultType[];
}): JSX.Element => (
  <ul className="offers">
    {results.map((result) => (
      <Offer
        canPrebookOffers={userRole == Role.redactor}
        key={result.id.raw}
        notify={notify}
        result={result}
      />
    ))}
  </ul>
)
