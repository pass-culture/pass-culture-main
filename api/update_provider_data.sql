update
    provider
set
    "bookingExternalUrl" = 'http://localhost:5003/tickets/create',
    "cancelExternalUrl" = 'http://localhost:5003/tickets/cancel',
    "notificationExternalUrl" = 'http://localhost:5003/tickets/notify',
    "hmacKey" = 'S3cr3tK3y'
where
    id = 104;