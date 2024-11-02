
# Link Click Tracking with Expiry

## What
Enables tracking the number of times a link is accessed before an expiry condition is met. Links can be configured to expire based on a time limit or click threshold.

### Classes/Functions
- **Link model**: The `click_count` and `expire_on` attributes manage click tracking and expiration.
- **track_click**: Increments the click count each time the link is accessed.
- **check_expiry**: Validates if a link has exceeded its click threshold or expiry date.

## How
### Example Usage
To create a link with a click limit or expiry date:

```bash
POST /links/create
Content-Type: application/json
{
    "long_url": "https://example.com",
    "title": "Example with Expiry",
    "click_limit": 100,
    "expire_on": "2024-12-31T23:59:59"
}
```
Response:
```json
{
    "message": "Link created successfully",
    "stub": "exp123"
}
```

## Why
Click tracking with expiration is useful for managing temporary campaigns or limited-access content. This feature provides control over link activity and allows for automated disabling when a link's lifecycle ends.
