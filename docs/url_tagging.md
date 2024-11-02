
# URL Tagging

## What
Allows users to add custom tags to URLs, enhancing their ability to organize, filter, and track URLs based on specific categories or campaigns.

### Classes/Functions
- **Link model**: Includes fields like `utm_source`, `utm_medium`, and `utm_campaign` for storing tag-related data.
- **Tagging Functionality**: Processes tag information during link creation, storing it for use in analytics and reporting.

## How
### Example Usage
To create a link with UTM tags for tracking:

```bash
POST /links/create
Content-Type: application/json
{
    "long_url": "https://campaign.com",
    "title": "Campaign Link",
    "utm_source": "newsletter",
    "utm_medium": "email",
    "utm_campaign": "spring_sale"
}
```
Response:
```json
{
    "message": "Link created with tags",
    "stub": "tag123"
}
```

## Why
Tagging enables more detailed insights into link performance by allowing users to attribute traffic sources and campaigns to individual links. This is essential for tracking marketing efficacy and user engagement across multiple channels.
