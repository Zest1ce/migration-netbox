# migration-netbox
Migrating data from phpIPAM to Netbox

# Create a credential.py file and provide the following values
```bash
# API configuration for NetBox
NETBOX_URL = "https://netbox.yoursite.com/api" # netbox service URL
NETBOX_API_TOKEN = "" # Token for accessing the phpIPAM API
```
```bash
# API configuration for phpIPAM
PHPIPAM_URL = 'https://ipam.yoursite.com/api' # phpIPAM service URL
PHPIPAM_APP_ID = '' # phpIPAM application ID
PHPIPAM_API_TOKEN = ''  # Token for accessing the phpIPAM API
```