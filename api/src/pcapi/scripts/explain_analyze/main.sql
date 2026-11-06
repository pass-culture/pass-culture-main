EXPLAIN ANALYZE
SELECT pricing_line.category                                                                         AS pricing_category,
       coalesce(educational_institution_program.name, CAST(educational_deposit.ministry AS VARCHAR)) AS ministry,
       sum(pricing_line.amount)                                                                      AS pricing_amount
FROM invoice
         JOIN invoice_cashflow AS invoice_cashflow_1 ON invoice.id = invoice_cashflow_1."invoiceId"
         JOIN cashflow ON cashflow.id = invoice_cashflow_1."cashflowId"
         JOIN cashflow_pricing AS cashflow_pricing_1 ON cashflow.id = cashflow_pricing_1."cashflowId"
         JOIN pricing ON pricing.id = cashflow_pricing_1."pricingId"
         JOIN pricing_line ON pricing.id = pricing_line."pricingId"
         JOIN finance_event ON finance_event.id = pricing."eventId"
         JOIN booking_finance_incident ON booking_finance_incident.id = finance_event."bookingFinanceIncidentId"
         JOIN collective_booking ON collective_booking.id = booking_finance_incident."collectiveBookingId"
         JOIN collective_stock ON collective_stock.id = collective_booking."collectiveStockId"
         JOIN educational_institution ON educational_institution.id = collective_booking."educationalInstitutionId"
         JOIN educational_deposit ON educational_deposit.id = collective_booking."educationalDepositId"
         LEFT OUTER JOIN educational_institution_program_association
                         ON educational_institution_program_association."institutionId" = educational_institution.id AND
                            (educational_institution_program_association.timespan @> collective_stock."startDatetime")
         LEFT OUTER JOIN educational_institution_program
                         ON educational_institution_program.id = educational_institution_program_association."programId"
WHERE invoice.id = 729740
GROUP BY pricing_line.category, educational_deposit.ministry, educational_institution_program.id;
