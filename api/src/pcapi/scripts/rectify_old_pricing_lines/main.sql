UPDATE pricing_line
SET amount = -amount
WHERE id IN (
    SELECT pricing_line.id
    FROM pricing_line
    JOIN pricing ON pricing_line."pricingId" = pricing.id
    JOIN finance_event ON pricing."eventId" = finance_event.id
    WHERE pricing_line.category = 'offerer contribution'
    AND pricing_line.amount < 0
    AND finance_event.motive = 'booking-used'
);