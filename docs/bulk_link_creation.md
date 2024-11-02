
# Bulk Link Creation

## What
This feature allows users to create multiple shortened links in a single request, enhancing efficiency and scalability. 
Users can define the long URLs and optional metadata like titles, expiry dates, and tags for each link.

### Classes/Functions
- **create_bulk_links**: Handles batch creation of links by processing a list of URLs and their attributes.
- **Link model**: Defines the attributes for each link, including `long_url`, `stub`, `title`, and metadata.

## How
### Example Usage
To create multiple links in bulk, use the following endpoint:

```bash
POST /links/create_bulk
Content-Type: application/json
{
    "links": [
        {"long_url": "https://example1.com", "title": "Example 1"},
        {"long_url": "https://example2.com", "title": "Example 2"}
    ]
}
```
Response:
```json
{
    "message": "Bulk link creation successful",
    "links": [{"stub": "abc123", "title": "Example 1"}, {"stub": "xyz456", "title": "Example 2"}]
}
```

## Why
The bulk creation feature streamlines link creation, enabling users to handle multiple URLs in one API call. This is especially valuable for campaigns or projects where numerous links need to be generated quickly. 
