UPDATE venue
   SET activity='OTHER'
 WHERE venue.id IN (
    SELECT venue.id
      FROM venue
      JOIN offerer ON offerer.id = venue."managingOffererId"
     WHERE offerer."validationStatus" IN ('REJECTED', 'CLOSED')
       AND (venue.activity IS NULL OR venue.activity='NOT_ASSIGNED')
    );