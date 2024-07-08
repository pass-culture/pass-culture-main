---
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# API resources pagination

## Overview
Our API is implementing **cursor-based pagination**. Cursor-based pagination uses a cursor (a pointer) to mark a specific position in the dataset, allowing the next page of results to be fetched starting from that point. 

We chose this type of pagination to **ensure efficient data retrieval** (using indexed columns avoids the overhead of skipping rows, leading to consistently fast queries even with large datasets) and to **reduce our database load**. 

:::info
In our API, **the cursor is always a resource `id`**.

_For instance, the `firstIndex` in the [**Get events endpoint**](/rest-api#tag/Event-offers/operation/GetEvents) is an event `id`_.
:::

:::note
This type of pagination has some drawbacks compared to the offset pagination:
- It is not possible to jump to an arbitrary page
- It is not possible to know in advance how many requests you need to execute to get all the items in a dataset

However, given the size of our tables, the performance gains outweigh those drawbacks.
:::

## Implementation examples

Here is an implementation example, showing how to fetch all the events for a specific venue.

<Tabs>
<TabItem value="python" label="Python">

```py
import os
import requests

# should come from an env variable (as it is a very sensitive data & as it varies between envs)
PASSCULTURE_API_KEY = os.getenv('PASSCULTURE_API_KEY')
# should vary between envs
PASSCULTURE_BASE_URI = "https://backend.integration.passculture.pro"

def fetch_all_events(venue_id: int, items_per_page: int = 50):
    all_data = []
    has_more_data = True
    params = {"venueId": venue_id, "limit": items_per_page}
    headers = {"Authorization": f"Bearer {PASSCULTURE_API_KEY}"}
    
    while has_more_data:
        response = requests.get(
            f"{PASSCULTURE_BASE_URI}/public/offers/v1/events",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

        data = response.json()
        events = data.get("events",[])
        all_data.extend(events)

        has_more_data = len(events) >= items_per_page

        if has_more_data:
            # Update params to fetch next page using the last event id + 1
            params["firstIndex"] = events[-1]["id"] + 1
    
    return all_data
```

</TabItem>

<TabItem value="javascript" label="Javascript">

```js
const axios = require('axios');

// should come from an env variable (as it is a very sensitive data & as it varies between envs)
const PASSCULTURE_API_KEY = process.env.PASSCULTURE_API_KEY;
// should vary between envs
const PASSCULTURE_BASE_URI = "https://backend.integration.passculture.pro";

async function fetchAllEvents(venueId, itemsPerPage = 50) {
    let allData = [];
    let hasMoreData = true;
    let params = { venueId, limit: itemsPerPage };
    let headers = { Authorization: `Bearer ${PASSCULTURE_API_KEY}` };
    
    while (hasMoreData) {
        const response = await axios.get(
            `${PASSCULTURE_BASE_URI}/public/offers/v1/events`,
            { headers, params }
        );

        if (response.status !== 200) {
            throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
        }

        const data = response.data;
        const events = data.events || [];

        allData = allData.concat(events);

        hasMoreData = events.length >= itemsPerPage

        if (hasMoreData) {
            // Update params to fetch next page using the last event id + 1
            params.firstIndex = events[events.length - 1].id + 1;
        } 
    }
}
```

</TabItem>
<TabItem value="php" label="PHP">

```php
<?php

require 'vendor/autoload.php'; // Assuming Guzzle is installed via Composer

use GuzzleHttp\Client;

// Environment variables
$PASSCULTURE_API_KEY = $_ENV['PASSCULTURE_API_KEY'];
$PASSCULTURE_BASE_URI = "https://backend.integration.passculture.pro";

function fetchAllEvents($venueId, $itemsPerPage = 50) {
    $allData = [];
    $hasMoreData = true;
    $params = ['venueId' => $venueId, 'limit' => $itemsPerPage];
    $headers = ['Authorization' => 'Bearer ' . $PASSCULTURE_API_KEY];
    
    $client = new Client([
        'base_uri' => $PASSCULTURE_BASE_URI,
        'headers' => $headers
    ]);

    while ($hasMoreData) {
        $response = $client->request('GET', '/public/offers/v1/events', [
            'query' => $params
        ]);

        $statusCode = $response->getStatusCode();
        
        if ($statusCode !== 200) {
            throw new Exception('Failed to fetch data: ' . $statusCode . ' ' . $response->getReasonPhrase());
        }

        $data = json_decode($response->getBody(), true);
        $events = $data['events'] ?? [];

        $allData = array_merge($allData, $events);

        $hasMoreData = count($events) >= $itemsPerPage;

        if ($hasMoreData) {
            // Update params to fetch next page using the last event id + 1
            $params['firstIndex'] = $events[count($events) - 1]['id'] + 1;
        }
       
    }

    return $allData;
}
```

</TabItem>

</Tabs>

